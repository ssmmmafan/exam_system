from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from exams.models import Exam, ExamQuestion
from teachers.models import Question
from students.models import StudentExamRecord, StudentProfile
import json


def get_exam_questions(exam):
    exam_questions = ExamQuestion.objects.filter(exam=exam).order_by('order')
    question_ids = [eq.question_id for eq in exam_questions]
    questions = Question.objects.filter(id__in=question_ids)
    
    question_map = {q.id: q for q in questions}
    ordered_questions = []
    
    for eq in exam_questions:
        if eq.question_id in question_map:
            question = question_map[eq.question_id]
            ordered_questions.append((question, eq.score))
    
    return ordered_questions


def get_options_from_question(question):
    options = []
    if question.type in ['single', 'multiple']:
        if isinstance(question.options, dict):
            for key in sorted(question.options.keys()):
                options.append({'key': key, 'value': question.options[key]})
        else:
            options = []
    return options


def get_options_dict_from_question(question):
    options = {}
    if question.type in ['single', 'multiple']:
        if isinstance(question.options, dict):
            options = question.options
        elif isinstance(question.options, str):
            try:
                options = json.loads(question.options)
            except (json.JSONDecodeError, ValueError):
                options = {}
        else:
            options = {}
    return options


def is_answer_correct(user_answer, correct_answer, question_type):
    if isinstance(user_answer, list):
        user_answer = ','.join(sorted(user_answer))
    user_answer = str(user_answer).strip()
    correct_answer = str(correct_answer).strip()
    
    if question_type in ('essay', 'discussion'):
        return None
    
    if question_type == 'multiple':
        user_set = set(user_answer.upper().replace(',', ''))
        correct_set = set(correct_answer.upper().replace(',', ''))
        return user_set == correct_set
    else:
        return user_answer.lower() == correct_answer.lower()


def dashboard_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    now = timezone.now()
    student = request.user
    
    upcoming_exams = Exam.objects.filter(
        is_published=True,
        start_time__gt=now
    ).order_by('start_time')[:5]
    
    completed_records = StudentExamRecord.objects.filter(
        student=student,
        is_finished=True
    ).order_by('-submit_time')[:5]
    
    missed_exams = Exam.objects.filter(
        is_published=True,
        end_time__lt=now
    ).exclude(
        id__in=StudentExamRecord.objects.filter(student=student).values('exam_id')
    )
    
    completed_count = StudentExamRecord.objects.filter(
        student=student,
        is_finished=True
    ).count()
    
    wrong_count = 0
    profile, _ = StudentProfile.objects.get_or_create(user=student)
    deleted_ids = set(profile.deleted_wrong_ids or [])
    for record in StudentExamRecord.objects.filter(student=student, is_finished=True):
        for question, _ in get_exam_questions(record.exam):
            if question.type in ('essay', 'discussion'):
                continue
            question_key = f'{record.exam.id}_{question.id}'
            if question_key in deleted_ids:
                continue
            raw_answer = record.answers.get(str(question.id), '')
            if isinstance(raw_answer, list):
                user_answer = ','.join(sorted(raw_answer))
            else:
                user_answer = str(raw_answer).strip()
            correct_answer = str(question.answer).strip()
            
            if not is_answer_correct(user_answer, correct_answer, question.type):
                wrong_count += 1
    
    upcoming_data = []
    for exam in upcoming_exams:
        upcoming_data.append({
            'id': exam.id,
            'title': exam.title,
            'start_time': exam.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': exam.end_time.strftime('%Y-%m-%d %H:%M'),
            'duration': exam.duration,
        })
    
    recent_results = []
    for record in completed_records:
        recent_results.append({
            'id': record.id,
            'exam_title': record.exam.title,
            'score': record.score,
            'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'stats': {
            'upcomingExams': upcoming_exams.count(),
            'completedExams': completed_count,
            'missedExams': missed_exams.count(),
            'wrongQuestions': wrong_count,
        },
        'upcoming_exams': upcoming_data,
        'recent_results': recent_results,
        'now': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


def exams_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    now = timezone.now()
    student = request.user
    
    all_exams = Exam.objects.filter(is_published=True).order_by('-start_time')
    
    exams_data = []
    for exam in all_exams:
        try:
            record = StudentExamRecord.objects.get(student=student, exam=exam)
            has_taken = record.is_finished
            record_score = record.score if record.is_finished else None
            record_id = record.id if record.is_finished else None
            time_spent = record.time_spent if record.is_finished else None
            needs_grading = record.is_finished and record.reviewed_at is None
        except StudentExamRecord.DoesNotExist:
            has_taken = False
            record_score = None
            record_id = None
            time_spent = None
            needs_grading = False
        
        eqs = ExamQuestion.objects.filter(exam=exam)
        question_ids = [eq.question_id for eq in eqs]
        questions = Question.objects.filter(id__in=question_ids)
        
        has_essay = questions.filter(type__in=['essay', 'discussion']).exists()
        needs_grading = needs_grading and has_essay
        
        type_counts = {
            'single': questions.filter(type='single').count(),
            'multiple': questions.filter(type='multiple').count(),
            'judge': questions.filter(type='judge').count(),
            'fill': questions.filter(type='fill').count(),
            'essay': questions.filter(type='essay').count(),
            'discussion': questions.filter(type='discussion').count(),
        }
        
        exams_data.append({
            'id': exam.id,
            'title': exam.title,
            'description': exam.description,
            'start_time': exam.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': exam.end_time.strftime('%Y-%m-%d %H:%M'),
            'duration': exam.duration,
            'total_score': exam.total_score,
            'question_count': len(question_ids),
            'type_counts': type_counts,
            'has_taken': has_taken,
            'is_completed': exam.end_time < now,
            'score': record_score,
            'record_id': record_id,
            'time_spent': time_spent,
            'needs_grading': needs_grading,
        })
    
    return JsonResponse({'exams': exams_data})


def exam_detail_api(request, exam_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    
    try:
        record = StudentExamRecord.objects.get(student=request.user, exam=exam)
        has_taken = record.is_finished
        record_score = record.score if record.is_finished else None
        record_id = record.id
        needs_grading = record.is_finished and record.reviewed_at is None
        now = timezone.now()
        if record.start_time:
            record_deadline = record.start_time + timedelta(minutes=exam.duration)
            record_deadline_str = record_deadline.strftime('%Y-%m-%d %H:%M')
            record_start_time_str = record.start_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            record_deadline_str = None
            record_start_time_str = None
    except StudentExamRecord.DoesNotExist:
        has_taken = False
        record_score = None
        record_id = None
        needs_grading = False
        record_deadline_str = None
        record_start_time_str = None
    
    eqs = ExamQuestion.objects.filter(exam=exam)
    question_ids = [eq.question_id for eq in eqs]
    questions = Question.objects.filter(id__in=question_ids)
    
    has_essay = questions.filter(type__in=['essay', 'discussion']).exists()
    needs_grading = needs_grading and has_essay
    
    type_counts = {
        'single': questions.filter(type='single').count(),
        'multiple': questions.filter(type='multiple').count(),
        'judge': questions.filter(type='judge').count(),
        'fill': questions.filter(type='fill').count(),
        'essay': questions.filter(type='essay').count(),
        'discussion': questions.filter(type='discussion').count(),
    }
    
    return JsonResponse({
        'id': exam.id,
        'title': exam.title,
        'description': exam.description,
        'start_time': exam.start_time.strftime('%Y-%m-%d %H:%M'),
        'end_time': exam.end_time.strftime('%Y-%m-%d %H:%M'),
        'duration': exam.duration,
        'total_score': exam.total_score,
        'question_count': len(question_ids),
        'type_counts': type_counts,
        'is_published': exam.is_published,
        'has_taken': has_taken,
        'score': record_score,
        'record_id': record_id,
        'needs_grading': needs_grading,
        'record_start_time': record_start_time_str,
        'record_deadline': record_deadline_str,
    })


def exam_taking_api(request, exam_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        exam = Exam.objects.get(id=exam_id, is_published=True)
    except Exam.DoesNotExist:
        try:
            exam = Exam.objects.get(id=exam_id)
            record = StudentExamRecord.objects.get(student=request.user, exam=exam)
            if record.is_finished:
                return JsonResponse({'error': '已提交', 'record_id': record.id}, status=400)
            return JsonResponse({'error': '考试已结束'}, status=400)
        except (Exam.DoesNotExist, StudentExamRecord.DoesNotExist):
            return JsonResponse({'error': 'Exam not found'}, status=404)

    now = timezone.now()
    if now >= exam.end_time:
        return JsonResponse({'error': '考试已结束，无法参加'}, status=400)

    record, created = StudentExamRecord.objects.get_or_create(
        student=request.user,
        exam=exam,
        defaults={'answers': {}, 'start_time': timezone.now()}
    )

    if record.is_finished:
        return JsonResponse({
            'error': '已提交',
            'record_id': record.id,
        }, status=400)

    if record.start_time and record.start_time + timedelta(minutes=exam.duration) < now:
        record.start_time = now
        record.is_finished = False
        record.answers = {}
        record.score = None
        record.submit_time = None
        record.time_spent = 0
        record.save()

    questions_data = []

    for question, score in get_exam_questions(exam):
        options = get_options_dict_from_question(question)

        questions_data.append({
            'id': question.id,
            'type': question.type,
            'content': question.content,
            'options': options,
            'score': score,
            'order': ExamQuestion.objects.get(exam=exam, question_id=question.id).order,
        })

    if record.start_time is None:
        record.start_time = now
        record.save()
        remaining_seconds = exam.duration * 60
    else:
        deadline = record.start_time + timedelta(minutes=exam.duration)
        remaining_seconds = max(0, (deadline - now).total_seconds())

    deadline = (record.start_time + timedelta(minutes=exam.duration)) if record.start_time else None
    deadline_str = deadline.strftime('%Y-%m-%d %H:%M:%S') if deadline else None

    return JsonResponse({
        'exam': {
            'id': exam.id,
            'title': exam.title,
            'duration': exam.duration,
            'total_score': exam.total_score,
        },
        'questions': questions_data,
        'record_id': record.id,
        'answers': record.answers,
        'time_left': int(remaining_seconds),
        'start_time': record.start_time.strftime('%Y-%m-%d %H:%M:%S') if record.start_time else None,
        'deadline': deadline_str,
    })


@csrf_exempt
def save_answer_api(request, exam_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    
    record, created = StudentExamRecord.objects.get_or_create(
        student=request.user,
        exam=exam,
        defaults={'answers': {}, 'start_time': timezone.now()}
    )
    
    if record.is_finished:
        return JsonResponse({'error': '已提交'}, status=400)
    
    record.answers.update(answers)
    record.save()
    
    return JsonResponse({'status': 'success', 'message': 'Answers saved'})


@csrf_exempt
def submit_exam_api(request, exam_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    
    try:
        record = StudentExamRecord.objects.get(
            student=request.user,
            exam=exam
        )
    except StudentExamRecord.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    if record.is_finished:
        return JsonResponse({'error': 'Exam already submitted', 'record_id': record.id}, status=400)
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    record.answers = answers
    record.is_finished = True
    record.submit_time = timezone.now()
    if record.start_time:
        record.time_spent = int((record.submit_time - record.start_time).total_seconds())
    
    score = 0
    for question, eq_score in get_exam_questions(exam):
        if question.type in ('essay', 'discussion'):
            continue
        user_answer = answers.get(str(question.id), '')
        if isinstance(user_answer, list):
            user_answer = ','.join(sorted(user_answer))
        user_answer = str(user_answer).strip()
        correct_answer = str(question.answer).strip()
        
        if is_answer_correct(user_answer, correct_answer, question.type):
            score += eq_score
    
    record.score = score
    record.save()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Exam submitted',
        'score': score,
        'total_score': exam.total_score,
        'record_id': record.id,
    })


def exam_result_api(request, record_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        record = StudentExamRecord.objects.get(id=record_id, student=request.user)
    except StudentExamRecord.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    exam = record.exam
    
    question_results = []
    for question, score in get_exam_questions(exam):
        user_answer = record.answers.get(str(question.id), '')
        if isinstance(user_answer, list):
            user_answer = ','.join(sorted(user_answer))
        options = get_options_dict_from_question(question)
        
        is_graded = record.reviewed_at is not None
        essay_scores = record.answers.get('_essay_scores', {}) if record.answers else {}
        
        if question.type in ('essay', 'discussion'):
            essay_score = essay_scores.get(str(question.id))
            if is_graded and essay_score is not None:
                is_correct = int(essay_score) > 0
            else:
                is_correct = None
        else:
            is_correct = is_answer_correct(
                user_answer,
                question.answer,
                question.type
            )
        
        question_results.append({
            'id': question.id,
            'type': question.type,
            'content': question.content,
            'options': options,
            'user_answer': user_answer,
            'correct_answer': question.answer,
            'score': score,
            'is_correct': is_correct,
            'essay_score': essay_scores.get(str(question.id)) if is_graded and question.type in ('essay', 'discussion') else None,
        })
    
    is_graded = record.reviewed_at is not None
    
    return JsonResponse({
        'exam': {
            'title': exam.title,
            'total_score': exam.total_score,
            'duration': exam.duration,
            'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M') if record.submit_time else None,
        },
        'record': {
            'score': record.score or 0,
            'total_score': exam.total_score,
            'duration': exam.duration,
            'time_spent': record.time_spent or 0,
            'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M:%S') if record.submit_time else None,
            'is_graded': is_graded,
        },
        'questions': question_results,
    })


def results_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    student = request.user
    
    records = StudentExamRecord.objects.filter(
        student=student,
        is_finished=True
    ).select_related('exam').order_by('-submit_time')
    
    results_data = []
    for record in records:
        exam_questions = get_exam_questions(record.exam)
        total_questions = len(exam_questions)
        correct_count = 0
        
        for question, _ in exam_questions:
            if question.type in ('essay', 'discussion'):
                continue
            raw_answer = record.answers.get(str(question.id), '')
            if isinstance(raw_answer, list):
                user_answer = ','.join(sorted(raw_answer))
            else:
                user_answer = str(raw_answer).strip()
            correct_answer = str(question.answer).strip()
            
            if is_answer_correct(user_answer, correct_answer, question.type):
                correct_count += 1
        
        accuracy = round((correct_count / total_questions * 100), 1) if total_questions > 0 else 0
        
        results_data.append({
            'id': record.id,
            'exam_id': record.exam.id,
            'exam_title': record.exam.title,
            'score': record.score,
            'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M'),
            'time_spent': record.time_spent,
            'accuracy': accuracy,
        })
    
    return JsonResponse({'results': results_data})


def wrong_questions_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    student = request.user
    
    profile, _ = StudentProfile.objects.get_or_create(user=student)
    deleted_ids = set(profile.deleted_wrong_ids or [])
    
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    try:
        page = int(page)
        page_size = int(page_size)
    except (ValueError, TypeError):
        page = 1
        page_size = 10
    
    records = StudentExamRecord.objects.filter(
        student=student,
        is_finished=True
    ).select_related('exam')
    
    wrong_questions = []
    
    for record in records:
        for question, _ in get_exam_questions(record.exam):
            if question.type in ('essay', 'discussion'):
                continue
            
            question_key = f'{record.exam.id}_{question.id}'
            if question_key in deleted_ids:
                continue
            
            raw_answer = record.answers.get(str(question.id), '')
            if isinstance(raw_answer, list):
                student_answer = ','.join(sorted(raw_answer))
            else:
                student_answer = str(raw_answer).strip()
            correct_answer = str(question.answer).strip()
            
            is_correct = is_answer_correct(student_answer, correct_answer, question.type)
            
            if not is_correct:
                options = get_options_dict_from_question(question)
                
                wrong_questions.append({
                    'question_key': question_key,
                    'exam_id': record.exam.id,
                    'question_id': question.id,
                    'exam_title': record.exam.title,
                    'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M'),
                    'type': question.type,
                    'content': question.content,
                    'options': options,
                    'answer': correct_answer,
                    'student_answer': student_answer,
                    'analysis': question.analysis or '',
                })
    
    total = len(wrong_questions)
    start = (page - 1) * page_size
    end = start + page_size
    paged_questions = wrong_questions[start:end]
    
    return JsonResponse({
        'wrong_questions': paged_questions,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': max(1, (total + page_size - 1) // page_size),
    })


@csrf_exempt
def delete_wrong_question_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        question_key = data.get('question_key')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not question_key:
        return JsonResponse({'error': 'question_key is required'}, status=400)
    
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    deleted = list(profile.deleted_wrong_ids or [])
    if question_key not in deleted:
        deleted.append(question_key)
        profile.deleted_wrong_ids = deleted
        profile.save()
    
    return JsonResponse({'status': 'success', 'message': 'Wrong question deleted'})


@csrf_exempt
def profile_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method == 'GET':
        student = request.user
        try:
            profile = StudentProfile.objects.get(user=student)
            profile_data = {
                'username': student.username,
                'student_id': profile.student_id,
                'class_name': profile.class_name,
                'major': profile.major,
                'enrollment_year': profile.enrollment_year,
                'phone': profile.phone,
                'teacher_name': profile.teacher.username if profile.teacher else None,
                'avatar': request.build_absolute_uri(profile.avatar.url) if profile.avatar else None,
            }
        except StudentProfile.DoesNotExist:
            profile_data = {
                'username': student.username,
                'student_id': '',
                'class_name': '',
                'major': '',
                'enrollment_year': '',
                'phone': '',
                'teacher_name': None,
                'avatar': None,
            }
        
        return JsonResponse({'profile': profile_data})
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            student = request.user
            
            profile, created = StudentProfile.objects.get_or_create(
                user=student,
                defaults={
                    'student_id': data.get('student_id', ''),
                    'class_name': data.get('class_name', ''),
                    'major': data.get('major', ''),
                    'enrollment_year': data.get('enrollment_year'),
                    'phone': data.get('phone', ''),
                }
            )
            
            if not created:
                if 'student_id' in data:
                    profile.student_id = data['student_id']
                if 'class_name' in data:
                    profile.class_name = data['class_name']
                if 'major' in data:
                    profile.major = data['major']
                if 'enrollment_year' in data:
                    profile.enrollment_year = data['enrollment_year']
                if 'phone' in data:
                    profile.phone = data['phone']
                profile.save()
            
            return JsonResponse({'status': 'success', 'message': 'Profile updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def avatar_upload_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if 'avatar' in request.FILES:
        profile.avatar = request.FILES['avatar']
        profile.save()
        return JsonResponse({
            'status': 'success',
            'avatar_url': request.build_absolute_uri(profile.avatar.url),
        })
    return JsonResponse({'error': 'No image file provided'}, status=400)