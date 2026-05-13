from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import re
from .models import StudentProfile, StudentExamRecord
from exams.models import Exam, ExamQuestion
from django.core.cache import cache
from teachers.models import Question


def get_question_with_content(exam_questions, random_options=False):
    """获取题目详细信息，支持随机选项顺序"""
    # 提取所有题目ID
    question_ids = [eq.question_id for eq in exam_questions]
    
    # 批量获取题目信息，减少数据库查询次数
    questions_dict = {q.id: q for q in Question.objects.filter(id__in=question_ids)}

    # 获取完整的题目信息
    questions_with_content = []
    for eq in exam_questions:
        question = questions_dict.get(eq.question_id)
        if question:
            # 随机选项顺序
            if random_options and question.options:
                import random
                options_list = list(question.options.items())
                random.shuffle(options_list)
                question.shuffled_options = dict(options_list)
            else:
                question.shuffled_options = question.options
                
            questions_with_content.append({
                'eq': eq,
                'question': question,
            })
        else:
            # 题目不存在的情况
            questions_with_content.append({
                'eq': eq,
                'question': None,
            })
    return questions_with_content
def register_view(request):
    """学生注册页面"""
    if request.user.is_authenticated:
        return redirect('students:dashboard')

    if request.method == 'POST':
        # 获取表单数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        student_id = request.POST.get('student_id')
        email = request.POST.get('email')
        class_name = request.POST.get('class_name')
        major = request.POST.get('major')

        # 验证数据
        error = False

        if not username or len(username) < 3:
            messages.error(request, '用户名至少3个字符')
            error = True

        if not password or len(password) < 6:
            messages.error(request, '密码至少6个字符')
            error = True
        elif password != password2:
            messages.error(request, '两次密码输入不一致')
            error = True

        if not student_id:
            messages.error(request, '学号不能为空')
            error = True

        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messages.error(request, '邮箱格式不正确')
            error = True

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在，请换一个')
            error = True

        if StudentProfile.objects.filter(student_id=student_id).exists():
            messages.error(request, '学号已存在，请确认')
            error = True

        if error:
            context = {
                'username': username,
                'student_id': student_id,
                'email': email,
                'class_name': class_name,
                'major': major,
            }
            return render(request, 'students/register.html', context)

        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # 创建学生档案
        StudentProfile.objects.create(
            user=user,
            student_id=student_id,
            class_name=class_name,
            major=major
        )

        messages.success(request, '🎉 注册成功！请登录')
        return redirect('login')

    return render(request, 'students/register.html')


@login_required
def dashboard(request):
    """学生主页：显示待考、已考列表"""
    if request.user.is_staff:
        messages.warning(request, '教师账号请使用教师后台')
        return redirect('/admin/')

    now = timezone.now()

    # 获取所有已发布的考试
    all_published_exams = Exam.objects.filter(is_published=True)
    
    # 获取学生已完成的考试ID
    completed_exam_ids = StudentExamRecord.objects.filter(
        student=request.user,
        is_finished=True
    ).values_list('exam_id', flat=True)
    
    # 待参加的考试（未完成且在时间范围内）
    upcoming_exams = all_published_exams.exclude(
        id__in=completed_exam_ids
    ).filter(
        end_time__gte=now
    ).order_by('start_time')
    
    # 已结束但未参加的考试（未完成但已过期）
    missed_exams = all_published_exams.exclude(
        id__in=completed_exam_ids
    ).filter(
        end_time__lt=now
    ).order_by('-end_time')
    
    # 已完成的考试记录
    completed_records = StudentExamRecord.objects.filter(
        student=request.user,
        is_finished=True
    ).select_related('exam').order_by('-submit_time')
    
    # 获取或创建学生档案
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        student_profile = StudentProfile.objects.create(
            user=request.user,
            student_id=f'TEMP{request.user.id}'
        )
    
    # 准备上下文数据
    context = {
        'upcoming_exams': upcoming_exams,
        'missed_exams': missed_exams,
        'completed_records': completed_records,
        'profile': student_profile,
        'now': now,
    }

    return render(request, 'students/dashboard.html', context)
@login_required
def exam_detail(request, exam_id):
    """考试详情页"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    now = timezone.now()

    if now < exam.start_time:
        messages.error(request, '考试还未开始')
        return redirect('students:dashboard')
    if now > exam.end_time:
        messages.error(request, '考试已结束')
        return redirect('students:dashboard')

    existing_record = StudentExamRecord.objects.filter(
        student=request.user,
        exam=exam,
        is_finished=True
    ).first()

    if existing_record:
        messages.warning(request, '你已经参加过这场考试')
        return redirect('students:exam_result', record_id=existing_record.id)

    record, created = StudentExamRecord.objects.get_or_create(
        student=request.user,
        exam=exam,
        defaults={'start_time': now}
    )

    question_count = exam.exam_questions.count()

    context = {
        'exam': exam,
        'record': record,
        'question_count': question_count,
        'now': now,
    }
    return render(request, 'students/exam_detail.html', context)


@login_required
def exam_taking(request, exam_id):
    """考试进行页"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    record = get_object_or_404(
        StudentExamRecord,
        student=request.user,
        exam=exam,
        is_finished=False
    )

    now = timezone.now()

    # 检查考试时间
    if now > exam.end_time:
        messages.error(request, '考试已结束，自动提交')
        return redirect('students:submit_exam', exam_id=exam.id)

    # 获取所有试题
    exam_questions = ExamQuestion.objects.filter(exam=exam).order_by('order')

    # 随机题目顺序
    if exam.random_questions:
        import random
        exam_questions = list(exam_questions)
        random.shuffle(exam_questions)

    # 获取完整的题目信息
    questions_with_content = get_question_with_content(exam_questions, exam.random_options)

    # 计算剩余时间
    time_delta = exam.end_time - now
    remaining_seconds = int(time_delta.total_seconds())
    if remaining_seconds < 0:
        remaining_seconds = 0

    # 处理POST请求（保存答案）
    if request.method == 'POST':
        answers = record.answers or {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                q_id = key.replace('question_', '')
                answers[q_id] = value

        record.answers = answers
        record.save()

        # 如果是AJAX请求，返回JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': '已保存'})

        messages.success(request, '答案已保存')
        return redirect('students:exam_taking', exam_id=exam.id)

    context = {
        'exam': exam,
        'record': record,
        'questions_with_content': questions_with_content,
        'now': now,
        'time_left': remaining_seconds,
    }
    return render(request, 'students/exam_taking.html', context)


@login_required
def submit_exam(request, exam_id):
    """提交考试 - 自动批改客观题，简答题待批改"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    record = get_object_or_404(
        StudentExamRecord,
        student=request.user,
        exam=exam,
        is_finished=False
    )

    if request.method == 'POST':
        # 更新最终答案
        answers = record.answers or {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                q_id = key.replace('question_', '')
                answers[q_id] = value

        # 计算客观题分数
        total_score = 0
        exam_questions = ExamQuestion.objects.filter(exam=exam)
        has_essay = False  # 👈 标记是否有简答题

        # 提取所有题目ID
        question_ids = [eq.question_id for eq in exam_questions]
        
        # 批量获取题目信息，减少数据库查询次数
        questions_dict = {q.id: q for q in Question.objects.filter(id__in=question_ids)}

        for eq in exam_questions:
            question = questions_dict.get(eq.question_id)
            if question:
                student_answer = answers.get(str(eq.question_id), '')

                if question.type == 'single':
                    if student_answer == question.answer:
                        total_score += eq.score

                elif question.type == 'multiple':
                    student_set = set(student_answer.split(',')) if student_answer else set()
                    correct_set = set(question.answer.split(','))
                    if student_set == correct_set:
                        total_score += eq.score

                elif question.type == 'judge':
                    if student_answer == question.answer:
                        total_score += eq.score

                elif question.type == 'fill':
                    if student_answer == question.answer:
                        total_score += eq.score

                elif question.type == 'essay':
                    has_essay = True  # 👈 标记有简答题

        # 更新记录
        record.answers = answers
        record.submit_time = timezone.now()
        record.is_finished = True

        # ✅ 关键修复
        if has_essay:
            record.score = None  # 有简答题，设为 None（待批改）
        else:
            record.score = total_score  # 只有客观题，直接给分

        record.save()

        if has_essay:
            messages.success(request, f'试卷提交成功！客观题得分：{total_score}，简答题待教师批改')
        else:
            messages.success(request, f'试卷提交成功！得分：{total_score}')

        return redirect('students:exam_result', record_id=record.id)

    context = {
        'exam': exam,
        'record': record,
    }
    return render(request, 'students/submit_confirm.html', context)
@login_required
def exam_result(request, record_id):
    """考试成绩页 - 学生查看自己的成绩，教师可以查看任何学生"""
    record = get_object_or_404(
        StudentExamRecord,
        id=record_id,
        is_finished=True
    )

    # ✅ 权限检查：学生只能看自己的，教师可以看所有
    if not request.user.is_staff and record.student != request.user:
        messages.error(request, '你没有权限查看其他学生的成绩')
        return redirect('students:dashboard')

    exam_questions = ExamQuestion.objects.filter(exam=record.exam).order_by('order')

    # 提取所有题目ID
    question_ids = [eq.question_id for eq in exam_questions]
    
    # 批量获取题目信息，减少数据库查询次数
    questions_dict = {q.id: q for q in Question.objects.filter(id__in=question_ids)}

    result_details = []
    has_essay_unscored = False

    for eq in exam_questions:
        question = questions_dict.get(eq.question_id)
        if question:
            student_answer = record.answers.get(str(eq.question_id), '')

            if question.type == 'essay':
                type_display = '简答题'
                score_key = f'score_{eq.question_id}'
                if score_key in record.answers:
                    score = int(record.answers[score_key])
                    is_scored = True
                else:
                    score = 0
                    is_scored = False
                    has_essay_unscored = True

                result_details.append({
                    'question_id': eq.question_id,
                    'student_answer': student_answer,
                    'correct_answer': question.answer,
                    'score': score,
                    'is_correct': False,
                    'is_essay': True,
                    'is_scored': is_scored,
                    'type_display': type_display,
                })

            elif question.type == 'single':
                is_correct = (student_answer == question.answer)
                result_details.append({
                    'question_id': eq.question_id,
                    'student_answer': student_answer,
                    'correct_answer': question.answer,
                    'score': eq.score if is_correct else 0,
                    'is_correct': is_correct,
                    'is_essay': False,
                    'is_scored': True,
                    'type_display': '单选题',
                })
            elif question.type == 'multiple':
                student_set = set(student_answer.split(',')) if student_answer else set()
                correct_set = set(question.answer.split(','))
                is_correct = (student_set == correct_set)
                result_details.append({
                    'question_id': eq.question_id,
                    'student_answer': student_answer,
                    'correct_answer': question.answer,
                    'score': eq.score if is_correct else 0,
                    'is_correct': is_correct,
                    'is_essay': False,
                    'is_scored': True,
                    'type_display': '多选题',
                })
            elif question.type == 'judge':
                is_correct = (student_answer == question.answer)
                result_details.append({
                    'question_id': eq.question_id,
                    'student_answer': student_answer,
                    'correct_answer': question.answer,
                    'score': eq.score if is_correct else 0,
                    'is_correct': is_correct,
                    'is_essay': False,
                    'is_scored': True,
                    'type_display': '判断题',
                })
            elif question.type == 'fill':
                is_correct = (student_answer == question.answer)
                result_details.append({
                    'question_id': eq.question_id,
                    'student_answer': student_answer,
                    'correct_answer': question.answer,
                    'score': eq.score if is_correct else 0,
                    'is_correct': is_correct,
                    'is_essay': False,
                    'is_scored': True,
                    'type_display': '填空题',
                })
            elif question.type == 'discussion':
                type_display = '论述题'
                score_key = f'score_{eq.question_id}'
                if score_key in record.answers:
                    score = int(record.answers[score_key])
                    is_scored = True
                else:
                    score = 0
                    is_scored = False
                    has_essay_unscored = True

                result_details.append({
                    'question_id': eq.question_id,
                    'student_answer': student_answer,
                    'correct_answer': question.answer,
                    'score': score,
                    'is_correct': False,
                    'is_essay': True,
                    'is_scored': is_scored,
                    'type_display': type_display,
                })

        else:
            result_details.append({
                'question_id': eq.question_id,
                'student_answer': '题目不存在',
                'correct_answer': '',
                'score': 0,
                'is_correct': False,
                'is_essay': False,
                'is_scored': False,
                'type_display': '未知',
            })
    total_score_display = record.score if record.score is not None else '待批改'
    context = {
        'record': record,
        'exam': record.exam,
        'result_details': result_details,
        'total_possible': sum(eq.score for eq in exam_questions),
        'has_essay_unscored': has_essay_unscored,
        'total_score_display': total_score_display,
    }
    return render(request, 'students/exam_result.html', context)


