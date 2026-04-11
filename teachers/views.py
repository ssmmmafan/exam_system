from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import HttpResponse
from .models import TeacherProfile, Question, QuestionTag
from exams.models import Exam, ExamQuestion
from students.models import StudentExamRecord

# 尝试导入pandas，如果失败则设置为None
try:
    import pandas as pd
    import io
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    io = None
    PANDAS_AVAILABLE = False


def get_questions_dict(question_ids):
    """批量获取题目信息，返回字典格式"""
    return {q.id: q for q in Question.objects.filter(id__in=question_ids)}


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

    # 提取所有题目ID
    question_ids = [eq.question_id for eq in exam_questions]
    
    # 批量获取题目信息，减少数据库查询次数
    questions_dict = get_questions_dict(question_ids)

    # 获取所有需要手动批改的题目（简答题、论述题）
    essay_questions = []
    for eq in exam_questions:
        question = questions_dict.get(eq.question_id)
        if question and question.type in ['essay', 'discussion']:
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

    if request.method == 'POST':
        # ✅ 第一步：计算客观题分数（从学生答案中计算）
        objective_score = 0
        for eq in exam_questions:
            question = questions_dict.get(eq.question_id)
            if question and question.type != 'essay':
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
                elif question.type == 'fill':
                    if student_answer == question.answer:
                        objective_score += eq.score

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


@login_required
def import_questions(request):
    """批量导入题目"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')

    if not PANDAS_AVAILABLE:
        messages.error(request, '批量导入功能需要安装pandas库，请联系管理员')
        return redirect('teachers:dashboard')

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        # 检查文件类型
        if not (file.name.endswith('.xlsx') or file.name.endswith('.csv')):
            messages.error(request, '请上传Excel或CSV文件')
            return redirect('teachers:import_questions')

        try:
            # 读取文件
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)

            # 验证必要列
            required_columns = ['type', 'content', 'answer', 'score']
            if not all(col in df.columns for col in required_columns):
                messages.error(request, '文件缺少必要列，请确保包含type、content、answer、score列')
                return redirect('teachers:import_questions')

            # 批量创建题目
            created_count = 0
            for _, row in df.iterrows():
                # 处理标签
                tags = []
                if 'tags' in row and pd.notna(row['tags']):
                    tag_names = [tag.strip() for tag in row['tags'].split(',')]
                    for tag_name in tag_names:
                        tag, _ = QuestionTag.objects.get_or_create(name=tag_name)
                        tags.append(tag)

                # 创建题目
                question = Question.objects.create(
                    type=row['type'],
                    content=row['content'],
                    answer=row['answer'],
                    score=int(row['score']),
                    created_by=request.user
                )

                # 添加标签
                if tags:
                    question.tags.add(*tags)

                created_count += 1

            messages.success(request, f'成功导入{created_count}道题目')
            clear_teacher_cache(request.user.id)
            return redirect('teachers:dashboard')

        except Exception as e:
            messages.error(request, f'导入失败：{str(e)}')
            return redirect('teachers:import_questions')

    return render(request, 'teachers/import_questions.html')


@login_required
def random_exam(request):
    """随机组卷"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')

    if request.method == 'POST':
        # 获取表单数据
        title = request.POST.get('title')
        description = request.POST.get('description')
        duration = int(request.POST.get('duration'))
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        total_score = int(request.POST.get('total_score'))
        random_questions = request.POST.get('random_questions') == 'on'
        random_options = request.POST.get('random_options') == 'on'
        enable_monitoring = request.POST.get('enable_monitoring') == 'on'
        
        # 题目配置
        question_config = {
            'single': int(request.POST.get('single_count', 0)),
            'multiple': int(request.POST.get('multiple_count', 0)),
            'judge': int(request.POST.get('judge_count', 0)),
            'essay': int(request.POST.get('essay_count', 0)),
            'fill': int(request.POST.get('fill_count', 0)),
            'discussion': int(request.POST.get('discussion_count', 0)),
        }
        
        # 创建考试
        exam = Exam.objects.create(
            title=title,
            description=description,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
            total_score=total_score,
            is_published=False,
            random_questions=random_questions,
            random_options=random_options,
            enable_monitoring=enable_monitoring,
            created_by=request.user
        )
        
        # 随机选择题目
        order = 1
        for q_type, count in question_config.items():
            if count > 0:
                # 筛选符合条件的题目
                questions = Question.objects.filter(
                    type=q_type,
                    created_by=request.user
                ).order_by('?')[:count]
                
                # 添加到考试
                for question in questions:
                    ExamQuestion.objects.create(
                        exam=exam,
                        question_id=question.id,
                        order=order,
                        score=question.score
                    )
                    order += 1
        
        messages.success(request, '随机组卷成功！')
        return redirect('teachers:dashboard')
    
    # 获取题型列表
    question_types = Question.QUESTION_TYPES
    
    context = {
        'question_types': question_types,
    }
    return render(request, 'teachers/random_exam.html', context)