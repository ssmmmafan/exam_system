from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
from .models import TeacherProfile, Question
from exams.models import Exam, ExamQuestion
from students.models import StudentExamRecord


def is_teacher(user):
    """检查用户是否为教师"""
    return user.is_authenticated and user.is_staff and not user.is_superuser


def clear_teacher_cache(user_id):
    """清除教师主页缓存"""
    cache_key = f'teacher_dashboard_{user_id}'
    cache.delete(cache_key)


@login_required
def dashboard(request):
    """教师主页 - 优化版（带缓存和查询优化）"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问教师页面')
        return redirect('/')

    # 尝试从缓存获取数据
    cache_key = f'teacher_dashboard_{request.user.id}'
    context = cache.get(cache_key)

    if context is None:
        # 缓存不存在，执行查询
        now = timezone.now()

        # ✅ 优化1：使用 only() 只查询需要的字段，count() 只查ID
        total_questions = Question.objects.filter(
            created_by=request.user
        ).only('id').count()

        total_exams = Exam.objects.filter(
            created_by=request.user
        ).only('id').count()

        ongoing_exams = Exam.objects.filter(
            created_by=request.user,
            start_time__lte=now,
            end_time__gte=now
        ).only('id').count()

        # 待批改的试卷
        pending_grading = StudentExamRecord.objects.filter(
            exam__created_by=request.user,
            is_finished=True,
            score__isnull=True
        ).only('id').count()

        # ✅ 优化2：最近数据只取5条，只查需要的字段
        recent_exams = Exam.objects.filter(
            created_by=request.user
        ).only(
            'id', 'title', 'created_at', 'is_published'
        ).order_by('-created_at')[:5]

        recent_questions = Question.objects.filter(
            created_by=request.user
        ).only(
            'id', 'type', 'content', 'created_at'
        ).order_by('-created_at')[:5]

        context = {
            'total_questions': total_questions,
            'total_exams': total_exams,
            'ongoing_exams': ongoing_exams,
            'pending_grading': pending_grading,
            'recent_exams': recent_exams,
            'recent_questions': recent_questions,
        }

        # ✅ 优化3：缓存5分钟
        cache.set(cache_key, context, 300)

    return render(request, 'teachers/dashboard.html', context)


@login_required
def pending_list(request):
    """待批改试卷列表"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')

    # 获取待批改的试卷（已完成但未评分）
    pending_records = StudentExamRecord.objects.filter(
        exam__created_by=request.user,
        is_finished=True,
        score__isnull=True
    ).select_related('student', 'exam').order_by('submit_time')

    # 分页
    paginator = Paginator(pending_records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_count': pending_records.count(),
    }
    return render(request, 'teachers/pending_list.html', context)


@login_required
@login_required
def grade_essay(request, record_id):
    """批改简答题页面"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')

    record = get_object_or_404(
        StudentExamRecord,
        id=record_id,
        exam__created_by=request.user,
        is_finished=True
    )

    exam = record.exam
    exam_questions = ExamQuestion.objects.filter(exam=exam).order_by('order')

    # 获取所有简答题
    essay_questions = []
    for eq in exam_questions:
        try:
            question = Question.objects.get(id=eq.question_id)
            if question.type == 'essay':
                student_answer = record.answers.get(str(eq.question_id), '')
                score_key = f'score_{eq.question_id}'
                existing_score = record.answers.get(score_key, None)
                if existing_score is not None:
                    existing_score = int(existing_score)

                essay_questions.append({
                    'eq': eq,
                    'question': question,
                    'student_answer': student_answer,
                    'max_score': eq.score,
                    'existing_score': existing_score,
                })
        except Question.DoesNotExist:
            pass

    if request.method == 'POST':
        # ✅ 第一步：计算客观题分数（从学生答案中计算）
        objective_score = 0
        for eq in exam_questions:
            try:
                question = Question.objects.get(id=eq.question_id)
                if question.type != 'essay':
                    student_answer = record.answers.get(str(eq.question_id), '')

                    if question.type == 'single':
                        if student_answer == question.answer:
                            objective_score += eq.score
                    elif question.type == 'multiple':
                        student_set = set(student_answer.split(',')) if student_answer else set()
                        correct_set = set(question.answer.split(','))
                        if student_set == correct_set:
                            objective_score += eq.score
                    elif question.type == 'judge':
                        if student_answer == question.answer:
                            objective_score += eq.score
            except Question.DoesNotExist:
                pass

        # ✅ 第二步：获取教师批改的简答题分数
        essay_score = 0
        scores = {}
        for eq in exam_questions:
            score_key = f'score_{eq.question_id}'
            if score_key in request.POST:
                try:
                    score = int(request.POST.get(score_key, 0))
                    scores[score_key] = score
                    essay_score += score
                except ValueError:
                    scores[score_key] = 0

        # ✅ 第三步：总分 = 客观题分数 + 简答题分数
        total_score = objective_score + essay_score

        # 更新记录
        record.score = total_score
        record.reviewed_at = timezone.now()
        record.reviewed_by = request.user

        # 保存各题得分（包括客观题和简答题的批改分数）
        answers = record.answers or {}
        answers.update(scores)
        record.answers = answers

        record.save()

        # 清除教师主页缓存
        clear_teacher_cache(request.user.id)

        messages.success(request, f'批改完成！客观题得分：{objective_score}，简答题得分：{essay_score}，总分：{total_score}')
        return redirect('teachers:pending_list')

    context = {
        'record': record,
        'exam': exam,
        'essay_questions': essay_questions,
    }
    return render(request, 'teachers/grade_essay.html', context)


@login_required
def ongoing_exams(request):
    """进行中的考试列表"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')

    now = timezone.now()

    # 进行中的考试
    ongoing = Exam.objects.filter(
        created_by=request.user,
        start_time__lte=now,
        end_time__gte=now,
        is_published=True
    ).order_by('start_time')

    # 即将开始的考试
    upcoming = Exam.objects.filter(
        created_by=request.user,
        start_time__gt=now,
        is_published=True
    ).order_by('start_time')

    # 已结束的考试
    ended = Exam.objects.filter(
        created_by=request.user,
        end_time__lt=now,
        is_published=True
    ).order_by('-end_time')

    context = {
        'ongoing': ongoing,
        'upcoming': upcoming,
        'ended': ended,
        'now': now,
    }
    return render(request, 'teachers/ongoing_exams.html', context)


@login_required
def exam_students(request, exam_id):
    """查看某场考试的所有学生成绩"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    records = StudentExamRecord.objects.filter(
        exam=exam,
        is_finished=True
    ).select_related('student').order_by('-submit_time')

    # 统计
    total_students = records.count()
    completed_students = records.filter(is_finished=True).count()
    avg_score = records.aggregate(models.Avg('score'))['score__avg'] or 0

    # 为每条记录添加状态
    for record in records:
        if record.score is None:
            record.status = '待批改'
            record.status_badge = 'warning'
        else:
            record.status = '已批改'
            record.status_badge = 'success'

    context = {
        'exam': exam,
        'records': records,
        'total_students': total_students,
        'completed_students': completed_students,
        'avg_score': round(avg_score, 1),
    }
    return render(request, 'teachers/exam_students.html', context)


@login_required
def student_result_detail(request, record_id):
    """教师查看学生成绩详情"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')

    # 获取记录，并确保是当前教师创建的考试
    record = get_object_or_404(
        StudentExamRecord,
        id=record_id,
        exam__created_by=request.user,
        is_finished=True
    )

    exam = record.exam
    exam_questions = ExamQuestion.objects.filter(exam=exam).order_by('order')

    result_details = []
    total_score = 0
    has_essay_unscored = False

    for eq in exam_questions:
        try:
            question = Question.objects.get(id=eq.question_id)
            student_answer = record.answers.get(str(eq.question_id), '')

            # 判断题型
            if question.type == 'essay':
                type_display = '简答题'
                score_key = f'score_{eq.question_id}'
                if score_key in record.answers:
                    score = int(record.answers[score_key])
                    is_scored = True
                    is_correct = False
                else:
                    score = 0
                    is_scored = False
                    has_essay_unscored = True
                    is_correct = False

                result_details.append({
                    'question': question,
                    'eq': eq,
                    'student_answer': student_answer,
                    'score': score,
                    'max_score': eq.score,
                    'is_correct': is_correct,
                    'is_essay': True,
                    'is_scored': is_scored,
                    'type_display': type_display,
                })
                total_score += score

            elif question.type == 'single':
                is_correct = (student_answer == question.answer)
                score = eq.score if is_correct else 0
                total_score += score
                result_details.append({
                    'question': question,
                    'eq': eq,
                    'student_answer': student_answer,
                    'score': score,
                    'max_score': eq.score,
                    'is_correct': is_correct,
                    'is_essay': False,
                    'is_scored': True,
                    'type_display': '单选题',
                })

            elif question.type == 'multiple':
                student_set = set(student_answer.split(',')) if student_answer else set()
                correct_set = set(question.answer.split(','))
                is_correct = (student_set == correct_set)
                score = eq.score if is_correct else 0
                total_score += score
                result_details.append({
                    'question': question,
                    'eq': eq,
                    'student_answer': student_answer,
                    'score': score,
                    'max_score': eq.score,
                    'is_correct': is_correct,
                    'is_essay': False,
                    'is_scored': True,
                    'type_display': '多选题',
                })

            elif question.type == 'judge':
                is_correct = (student_answer == question.answer)
                score = eq.score if is_correct else 0
                total_score += score
                result_details.append({
                    'question': question,
                    'eq': eq,
                    'student_answer': student_answer,
                    'score': score,
                    'max_score': eq.score,
                    'is_correct': is_correct,
                    'is_essay': False,
                    'is_scored': True,
                    'type_display': '判断题',
                })

        except Question.DoesNotExist:
            result_details.append({
                'question': None,
                'eq': eq,
                'student_answer': '题目不存在',
                'score': 0,
                'max_score': eq.score,
                'is_correct': False,
                'is_essay': False,
                'is_scored': False,
                'type_display': '未知',
            })

    # 确保记录的总分与计算一致
    if record.score != total_score and not has_essay_unscored:
        record.score = total_score
        record.save()

    context = {
        'record': record,
        'exam': exam,
        'student': record.student,
        'result_details': result_details,
        'total_score': total_score,
        'total_possible': sum(eq.score for eq in exam_questions),
        'has_essay_unscored': has_essay_unscored,
        'submitted_at': record.submit_time,
        'reviewed_at': record.reviewed_at,
        'reviewed_by': record.reviewed_by,
    }
    return render(request, 'teachers/student_result_detail.html', context)