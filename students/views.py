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
    """学生主页：显示待考、已考列表（带缓存优化）"""
    if request.user.is_staff:
        messages.warning(request, '教师账号请使用教师后台')
        return redirect('/admin/')

    now = timezone.now()

    # 尝试从缓存获取数据
    cache_key = f'student_dashboard_{request.user.id}'
    context = cache.get(cache_key)

    if not context:
        # 缓存不存在，执行查询
        print(f"从数据库查询数据 for user {request.user.id}")  # 调试用

        # 待参加的考试 - 使用子查询优化
        completed_exam_ids = StudentExamRecord.objects.filter(
            student=request.user,
            is_finished=True
        ).values_list('exam_id', flat=True)

        upcoming_exams = Exam.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_published=True
        ).exclude(
            id__in=completed_exam_ids
        ).only(
            'id', 'title', 'description', 'start_time', 'end_time', 'duration', 'total_score'
        ).order_by('start_time')[:10]

        # 已完成的考试
        completed_records = StudentExamRecord.objects.filter(
            student=request.user,
            is_finished=True
        ).select_related('exam').only(
            'id', 'score', 'submit_time', 'exam__id', 'exam__title', 'exam__total_score'
        ).order_by('-submit_time')[:10]

        # 获取或创建学生档案
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            profile = StudentProfile.objects.create(
                user=request.user,
                student_id=f'TEMP{request.user.id}'
            )

        # 准备上下文数据
        context = {
            'upcoming_exams': upcoming_exams,
            'completed_records': completed_records,
            'profile': profile,
            'now': now,
        }

        # 存入缓存，有效期5分钟（300秒）
        cache.set(cache_key, context, 300)
        print(f"数据已缓存 for user {request.user.id}")
    else:
        print(f"从缓存读取数据 for user {request.user.id}")

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

    if now > exam.end_time:
        messages.error(request, '考试已结束，自动提交')
        return redirect('students:submit_exam', exam_id=exam.id)

    exam_questions = ExamQuestion.objects.filter(exam=exam).order_by('order')

    if request.method == 'POST':
        answers = record.answers or {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                q_id = key.replace('question_', '')
                answers[q_id] = value

        record.answers = answers
        record.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': '已保存'})

        messages.success(request, '答案已保存')

    context = {
        'exam': exam,
        'record': record,
        'exam_questions': exam_questions,
        'now': now,
        'time_left': (exam.end_time - now).total_seconds(),
    }
    return render(request, 'students/exam_taking.html', context)


@login_required
def submit_exam(request, exam_id):
    """提交考试"""
    exam = get_object_or_404(Exam, id=exam_id)
    record = get_object_or_404(
        StudentExamRecord,
        student=request.user,
        exam=exam,
        is_finished=False
    )

    if request.method == 'POST':
        answers = record.answers or {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                q_id = key.replace('question_', '')
                answers[q_id] = value

        # 简单计分（假设每题5分）
        total_score = 0
        exam_questions = ExamQuestion.objects.filter(exam=exam)

        for eq in exam_questions:
            if str(eq.question_id) in answers:
                total_score += eq.score

        record.answers = answers
        record.score = total_score
        record.submit_time = timezone.now()
        record.is_finished = True
        record.save()

        messages.success(request, f'试卷提交成功！得分：{total_score}')
        return redirect('students:exam_result', record_id=record.id)

    context = {
        'exam': exam,
        'record': record,
    }
    return render(request, 'students/submit_confirm.html', context)


@login_required
def exam_result(request, record_id):
    """考试成绩页"""
    record = get_object_or_404(
        StudentExamRecord,
        id=record_id,
        student=request.user,
        is_finished=True
    )

    exam_questions = ExamQuestion.objects.filter(exam=record.exam).order_by('order')

    result_details = []
    for eq in exam_questions:
        student_answer = record.answers.get(str(eq.question_id), '')
        is_correct = bool(student_answer)  # 简单判断：有答案就算对

        result_details.append({
            'question_id': eq.question_id,
            'student_answer': student_answer,
            'score': eq.score if is_correct else 0,
            'is_correct': is_correct,
        })

    context = {
        'record': record,
        'exam': record.exam,
        'result_details': result_details,
        'total_possible': sum(eq.score for eq in exam_questions),
    }
    return render(request, 'students/exam_result.html', context)