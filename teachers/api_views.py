from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Sum, Q
from exams.models import Exam, ExamQuestion
from teachers.models import Question, TeacherProfile
from students.models import StudentExamRecord, StudentProfile
from django.contrib.auth.models import User
from students.api_views import is_answer_correct, get_exam_questions, get_options_dict_from_question
import json

@login_required
def dashboard_api(request):
    now = timezone.now()
    teacher = request.user
    
    total_questions = Question.objects.filter(created_by=teacher).count()
    total_exams = Exam.objects.filter(created_by=teacher).count()
    
    ongoing_exams = Exam.objects.filter(
        created_by=teacher,
        is_published=True,
        start_time__lte=now,
        end_time__gte=now
    ).count()
    
    pending_grading = StudentExamRecord.objects.filter(
        exam__created_by=teacher,
        is_finished=True,
        reviewed_at__isnull=True
    ).count()
    
    total_students = StudentProfile.objects.filter(teacher=teacher).count()
    
    recent_exams = Exam.objects.filter(
        created_by=teacher
    ).annotate(
        total_students=Count('student_records', distinct=True),
        finished_students=Count(
            'student_records',
            filter=Q(student_records__is_finished=True),
            distinct=True,
        ),
        graded_students=Count(
            'student_records',
            filter=Q(
                student_records__is_finished=True,
                student_records__reviewed_at__isnull=False,
            ),
            distinct=True,
        ),
    ).order_by('-created_at')[:5]

    exams_data = []
    for exam in recent_exams:
        exams_data.append({
            'id': exam.id,
            'title': exam.title,
            'status': 'ongoing' if (exam.start_time <= now <= exam.end_time) else \
                      'upcoming' if exam.start_time > now else 'ended',
            'total_students': exam.total_students,
            'finished_students': exam.finished_students,
            'graded_students': exam.graded_students,
            'created_at': exam.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    pending_records = StudentExamRecord.objects.filter(
        exam__created_by=teacher,
        is_finished=True,
        reviewed_at__isnull=True
    ).select_related('exam', 'student')[:5]
    
    pending_data = []
    for record in pending_records:
        pending_data.append({
            'id': record.id,
            'exam_title': record.exam.title,
            'student_name': record.student.username,
            'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'stats': {
            'total_questions': total_questions,
            'total_exams': total_exams,
            'ongoing_exams': ongoing_exams,
            'pending_grading': pending_grading,
            'total_students': total_students,
        },
        'recent_exams': exams_data,
        'pending_records': pending_data,
        'now': now.strftime('%Y-%m-%d %H:%M:%S'),
    })

@login_required
def question_stats_api(request):
    teacher = request.user
    
    min_difficulty = int(request.GET.get('min_difficulty', 1))
    max_difficulty = int(request.GET.get('max_difficulty', 5))
    
    questions = Question.objects.filter(
        created_by=teacher,
        difficulty__gte=min_difficulty,
        difficulty__lte=max_difficulty
    )
    
    stats = {
        'single': questions.filter(type='single').count(),
        'multiple': questions.filter(type='multiple').count(),
        'judge': questions.filter(type='judge').count(),
        'fill': questions.filter(type='fill').count(),
        'essay': questions.filter(type='essay').count(),
        'discussion': questions.filter(type='discussion').count(),
    }
    
    return JsonResponse(stats)

@login_required
def batch_delete_questions_api(request):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    questions = Question.objects.filter(id__in=ids, created_by=request.user)
    deleted_count = questions.count()
    questions.delete()
    
    return JsonResponse({
        'status': 'success',
        'deleted_count': deleted_count,
        'message': f'{deleted_count} questions deleted'
    })

@login_required
@csrf_exempt
def question_list_api(request):
    teacher = request.user
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        question_type = data.get('type')
        content = data.get('content')
        answer = data.get('answer')
        score = data.get('score', 5)
        analysis = data.get('analysis', '')
        difficulty = data.get('difficulty', 3)
        chapter = data.get('chapter', '')
        knowledge_point = data.get('knowledge_point', '')
        
        options = {}
        if question_type in ['single', 'multiple']:
            options_data = data.get('options', {})
            if isinstance(options_data, str):
                try:
                    options = json.loads(options_data)
                except json.JSONDecodeError:
                    options = {}
            elif isinstance(options_data, dict):
                options = options_data
        
        question = Question.objects.create(
            type=question_type,
            content=content,
            options=options,
            answer=answer,
            score=score,
            analysis=analysis,
            difficulty=difficulty,
            chapter=chapter,
            knowledge_point=knowledge_point,
            created_by=request.user,
        )
        
        return JsonResponse({
            'status': 'success',
            'question': {
                'id': question.id,
                'type': question.type,
                'content': question.content,
                'score': question.score,
                'difficulty': question.difficulty,
                'chapter': question.chapter,
                'knowledge_point': question.knowledge_point,
            },
        })
    
    questions = Question.objects.filter(created_by=teacher)
    
    type_filter = request.GET.get('type')
    if type_filter:
        questions = questions.filter(type=type_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        questions = questions.filter(content__icontains=search_query)
    
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    start = (page - 1) * per_page
    end = start + per_page
    
    questions_data = []
    for question in questions[start:end]:
        options = question.options if isinstance(question.options, dict) else {}
        
        questions_data.append({
            'id': question.id,
            'type': question.type,
            'content': question.content,
            'options': options,
            'answer': question.answer,
            'analysis': question.analysis,
            'score': question.score,
            'difficulty': question.difficulty,
            'chapter': question.chapter,
            'knowledge_point': question.knowledge_point,
            'tags': [],  # 简化处理，实际可以用 ManyToMany
            'created_at': question.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'questions': questions_data,
        'total': questions.count(),
        'page': page,
        'per_page': per_page,
    })

@login_required
@csrf_exempt
def question_detail_api(request, question_id):
    try:
        question = Question.objects.get(id=question_id, created_by=request.user)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        if 'type' in data:
            question.type = data['type']
        if 'content' in data:
            question.content = data['content']
        if 'answer' in data:
            question.answer = data['answer']
        if 'score' in data:
            question.score = data['score']
        if 'analysis' in data:
            question.analysis = data['analysis']
        if 'difficulty' in data:
            question.difficulty = data['difficulty']
        if 'chapter' in data:
            question.chapter = data['chapter']
        if 'knowledge_point' in data:
            question.knowledge_point = data['knowledge_point']
        
        if question.type in ['single', 'multiple'] and 'options' in data:
            options_data = data['options']
            if isinstance(options_data, str):
                try:
                    question.options = json.loads(options_data)
                except json.JSONDecodeError:
                    pass
            elif isinstance(options_data, dict):
                question.options = options_data
        
        question.save()
        
        return JsonResponse({'status': 'success', 'message': 'Question updated'})
    
    if request.method == 'DELETE':
        question.delete()
        return JsonResponse({'status': 'success', 'message': 'Question deleted'})
    
    options = question.options if isinstance(question.options, dict) else {}
    
    return JsonResponse({
        'id': question.id,
        'type': question.type,
        'content': question.content,
        'options': options,
        'answer': question.answer,
        'analysis': question.analysis,
        'score': question.score,
        'difficulty': question.difficulty,
        'chapter': question.chapter,
        'knowledge_point': question.knowledge_point,
        'tags': [],
    })

@login_required
def create_question_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    question_type = data.get('type')
    content = data.get('content')
    answer = data.get('answer')
    score = data.get('score', 5)
    analysis = data.get('analysis', '')
    difficulty = data.get('difficulty', 3)
    chapter = data.get('chapter', '')
    knowledge_point = data.get('knowledge_point', '')
    
    options = {}
    if question_type in ['single', 'multiple']:
        options_data = data.get('options', {})
        if isinstance(options_data, str):
            try:
                options = json.loads(options_data)
            except json.JSONDecodeError:
                options = {}
        elif isinstance(options_data, dict):
            options = options_data
    
    question = Question.objects.create(
        type=question_type,
        content=content,
        options=options,
        answer=answer,
        score=score,
        analysis=analysis,
        difficulty=difficulty,
        chapter=chapter,
        knowledge_point=knowledge_point,
        created_by=request.user,
    )
    
    return JsonResponse({
        'status': 'success',
        'question': {
            'id': question.id,
            'type': question.type,
            'content': question.content,
            'score': question.score,
            'difficulty': question.difficulty,
            'chapter': question.chapter,
            'knowledge_point': question.knowledge_point,
        },
    })

@login_required
def edit_question_api(request, question_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        question = Question.objects.get(id=question_id, created_by=request.user)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if 'type' in data:
        question.type = data['type']
    if 'content' in data:
        question.content = data['content']
    if 'answer' in data:
        question.answer = data['answer']
    if 'score' in data:
        question.score = data['score']
    if 'analysis' in data:
        question.analysis = data['analysis']
    if 'difficulty' in data:
        question.difficulty = data['difficulty']
    if 'chapter' in data:
        question.chapter = data['chapter']
    if 'knowledge_point' in data:
        question.knowledge_point = data['knowledge_point']
    
    if question.type in ['single', 'multiple'] and 'options' in data:
        options_data = data['options']
        if isinstance(options_data, str):
            try:
                question.options = json.loads(options_data)
            except json.JSONDecodeError:
                pass
        elif isinstance(options_data, dict):
            question.options = options_data
    
    question.save()
    
    return JsonResponse({'status': 'success', 'message': 'Question updated'})

@login_required
@csrf_exempt
def delete_question_api(request, question_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        question = Question.objects.get(id=question_id, created_by=request.user)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    
    question.delete()
    
    return JsonResponse({'status': 'success', 'message': 'Question deleted'})

@login_required
@csrf_exempt
def exam_list_api(request):
    teacher = request.user
    exams = Exam.objects.filter(created_by=teacher).order_by('-created_at')
    
    status_filter = request.GET.get('status')
    now = timezone.now()
    
    if status_filter == 'ongoing':
        exams = exams.filter(start_time__lte=now, end_time__gte=now, is_published=True)
    elif status_filter == 'published':
        exams = exams.filter(start_time__gt=now, is_published=True)
    elif status_filter == 'finished':
        exams = exams.filter(end_time__lt=now)
    elif status_filter == 'draft':
        exams = exams.filter(is_published=False)
    elif status_filter == 'pending_grading':
        exam_ids = StudentExamRecord.objects.filter(
            is_finished=True,
            reviewed_at__isnull=True,
            exam__in=exams
        ).values_list('exam_id', flat=True).distinct()
        exams = exams.filter(id__in=exam_ids)
    
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    start = (page - 1) * per_page
    end = start + per_page
    
    exams_data = []
    for exam in exams[start:end]:
        total_records = StudentExamRecord.objects.filter(exam=exam).count()
        finished_records = StudentExamRecord.objects.filter(
            exam=exam, is_finished=True
        ).count()
        pending_records = StudentExamRecord.objects.filter(
            exam=exam, is_finished=True, reviewed_at__isnull=True
        ).count()
        
        eqs = ExamQuestion.objects.filter(exam=exam)
        question_ids = [eq.question_id for eq in eqs]
        questions = Question.objects.filter(id__in=question_ids)
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
            'is_published': exam.is_published,
            'student_count': total_records,
            'finished_students': finished_records,
            'pending_grading_count': pending_records,
            'status': 'ongoing' if (exam.start_time <= now <= exam.end_time and exam.is_published) else \
                      'published' if (exam.start_time > now and exam.is_published) else \
                      'finished' if exam.end_time < now else 'draft',
        })
    
    return JsonResponse({
        'exams': exams_data,
        'total': exams.count(),
        'page': page,
        'per_page': per_page,
    })

@csrf_exempt
def exam_detail_api(request, exam_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        exam = Exam.objects.get(id=exam_id, created_by=request.user)
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    
    now = timezone.now()
    
    questions_data = []
    
    exam_questions = ExamQuestion.objects.filter(exam=exam).order_by('order')
    for eq in exam_questions:
        try:
            question = Question.objects.get(id=eq.question_id)
            options = {}
            if question.type in ['single', 'multiple']:
                if isinstance(question.options, dict):
                    options = question.options
                elif isinstance(question.options, str):
                    try:
                        options = json.loads(question.options)
                    except (json.JSONDecodeError, ValueError):
                        for i, option in enumerate(question.options.split('||')):
                            options[chr(65 + i)] = option.strip()
            
            questions_data.append({
                'id': question.id,
                'type': question.type,
                'content': question.content,
                'options': options,
                'answer': question.answer,
                'score': eq.score,
                'order': eq.order,
            })
        except Question.DoesNotExist:
            continue
    
    exam_records = StudentExamRecord.objects.filter(
        exam=exam
    ).select_related('student').order_by('-submit_time')
    
    records_data = []
    for record in exam_records:
        student_id = ''
        class_name = ''
        try:
            profile = StudentProfile.objects.get(user=record.student)
            student_id = profile.student_id
            class_name = profile.class_name
        except StudentProfile.DoesNotExist:
            pass
        
        records_data.append({
            'id': record.id,
            'student_id': student_id,
            'student_name': record.student.username,
            'class_name': class_name,
            'status': 'ongoing' if not record.is_finished else \
                      'graded' if record.reviewed_at else 'finished',
            'score': record.score,
            'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M') if record.submit_time else None,
        })
    
    exam_status = 'ongoing' if (exam.start_time <= now <= exam.end_time and exam.is_published) else \
                  'upcoming' if (exam.start_time > now and exam.is_published) else \
                  'ended' if exam.end_time < now else 'draft'
    
    type_counts = {}
    for q in questions_data:
        t = q['type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    return JsonResponse({
        'exam': {
            'id': exam.id,
            'title': exam.title,
            'description': exam.description,
            'start_time': exam.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': exam.end_time.strftime('%Y-%m-%d %H:%M'),
            'duration': exam.duration,
            'total_score': exam.total_score,
            'question_count': len(questions_data),
            'type_counts': type_counts,
            'student_count': exam_records.count(),
            'random_questions': exam.random_questions,
            'random_options': exam.random_options,
            'is_published': exam.is_published,
            'status': exam_status,
        },
        'questions': questions_data,
        'records': records_data,
    })

@login_required
@csrf_exempt
def create_exam_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    title = data.get('title')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    
    if not title or not start_time_str or not end_time_str:
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    try:
        start_time = timezone.datetime.fromisoformat(start_time_str)
        end_time = timezone.datetime.fromisoformat(end_time_str)
    except ValueError:
        try:
            start_time = timezone.datetime.fromisoformat(start_time_str + ':00')
            end_time = timezone.datetime.fromisoformat(end_time_str + ':00')
        except ValueError:
            return JsonResponse({'error': 'Invalid datetime format'}, status=400)
    
    exam = Exam.objects.create(
        title=title,
        description=data.get('description', ''),
        start_time=start_time,
        end_time=end_time,
        duration=data.get('duration', 120),
        created_by=request.user,
        random_questions=data.get('random_questions', False),
        random_options=data.get('random_options', False),
    )
    
    total_score = 0
    question_ids = data.get('question_ids', [])
    question_scores = data.get('question_scores', {})
    
    if question_ids:
        questions = Question.objects.filter(id__in=question_ids, created_by=request.user)
        for i, question in enumerate(questions):
            custom_score = question_scores.get(str(question.id)) or question_scores.get(question.id)
            score = custom_score if custom_score is not None else question.score
            ExamQuestion.objects.create(
                exam=exam,
                question_id=question.id,
                order=i + 1,
                score=score
            )
            total_score += score
    else:
        questions_data = data.get('questions', [])
        for i, q_data in enumerate(questions_data):
            question = Question.objects.create(
                type=q_data.get('type'),
                content=q_data.get('content'),
                options=q_data.get('options', {}),
                answer=q_data.get('answer'),
                score=q_data.get('score', 10),
                created_by=request.user,
            )
            ExamQuestion.objects.create(
                exam=exam,
                question_id=question.id,
                order=i + 1,
                score=question.score
            )
            total_score += question.score
    
    exam.total_score = total_score
    exam.question_count = ExamQuestion.objects.filter(exam=exam).count()
    exam.save()
    
    return JsonResponse({
        'status': 'success',
        'exam': {
            'id': exam.id,
            'title': exam.title,
            'total_score': exam.total_score,
            'question_count': exam.question_count,
        },
    })

@login_required
@csrf_exempt
def random_exam_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    exam = Exam.objects.create(
        title=data.get('title'),
        description=data.get('description', ''),
        start_time=timezone.datetime.fromisoformat(data.get('start_time')),
        end_time=timezone.datetime.fromisoformat(data.get('end_time')),
        duration=data.get('duration', 120),
        created_by=request.user,
        random_questions=data.get('random_questions', True),
        random_options=data.get('random_options', True),
    )
    
    question_spec = data.get('question_spec', {})
    min_difficulty = data.get('min_difficulty', 1)
    max_difficulty = data.get('max_difficulty', 5)
    
    selected_questions = []
    
    for q_type, count in question_spec.items():
        if count > 0:
            questions = Question.objects.filter(
                created_by=request.user,
                type=q_type,
                difficulty__gte=min_difficulty,
                difficulty__lte=max_difficulty
            ).order_by('?')[:count]
            selected_questions.extend(list(questions))
    
    total_score = 0
    for i, question in enumerate(selected_questions):
        ExamQuestion.objects.create(
            exam=exam,
            question_id=question.id,
            order=i + 1,
            score=question.score
        )
        total_score += question.score
    
    exam.total_score = total_score
    exam.question_count = ExamQuestion.objects.filter(exam=exam).count()
    exam.save()
    
    return JsonResponse({
        'status': 'success',
        'exam': {
            'id': exam.id,
            'title': exam.title,
            'total_score': exam.total_score,
            'question_count': exam.question_count,
        },
        'selected_questions': len(selected_questions),
    })

@login_required
@csrf_exempt
def publish_exam_api(request, exam_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        exam = Exam.objects.get(id=exam_id, created_by=request.user)
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    
    # 只有草稿可以发布
    if exam.is_published:
        return JsonResponse({'error': 'Exam is already published'}, status=400)
    
    exam.is_published = True
    exam.save()
    
    student_profiles = StudentProfile.objects.all()
    created_count = 0
    for profile in student_profiles:
        _, created = StudentExamRecord.objects.get_or_create(
            student=profile.user,
            exam=exam,
            defaults={'answers': {}}
        )
        if created:
            created_count += 1
    
    return JsonResponse({'status': 'success', 'message': 'Exam published', 'created_records': created_count})

@login_required
@csrf_exempt
def unpublish_exam_api(request, exam_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        exam = Exam.objects.get(id=exam_id, created_by=request.user)
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    
    now = timezone.now()
    
    # 只有未结束的考试可以取消发布
    if exam.end_time < now:
        return JsonResponse({'error': 'Cannot unpublish finished exam'}, status=400)
    
    exam.is_published = False
    exam.save()
    
    # 获取所有正在考试的学生记录
    ongoing_records = StudentExamRecord.objects.filter(
        exam=exam, 
        start_time__isnull=False,
        is_finished=False
    )
    
    # 强制结束正在考试的学生
    for record in ongoing_records:
        record.is_finished = True
        record.submit_time = timezone.now()
        # 如果有答案，计算客观题分数
        if record.answers:
            try:
                answers = json.loads(record.answers) if isinstance(record.answers, str) else record.answers
                score = 0
                exam_questions = ExamQuestion.objects.filter(exam=exam).order_by('order')
                for eq in exam_questions:
                    question = Question.objects.get(id=eq.question_id)
                    user_answer = answers.get(str(eq.question_id))
                    if user_answer:
                        if question.type in ['single', 'judge']:
                            if str(user_answer).strip() == str(question.answer).strip():
                                score += eq.score
                        elif question.type == 'multiple':
                            user_ans = set(str(user_answer).split(','))
                            correct_ans = set(str(question.answer).split(','))
                            if user_ans == correct_ans:
                                score += eq.score
                record.score = score
            except Exception:
                record.score = 0
        record.save()
    
    # 删除未开始的考试记录
    StudentExamRecord.objects.filter(exam=exam, start_time__isnull=True).delete()
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Exam unpublished',
        'forced_students': ongoing_records.count()
    })

@login_required
@csrf_exempt
def delete_exam_api(request, exam_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        exam = Exam.objects.get(id=exam_id, created_by=request.user)
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    
    # 安全保护：只允许删除草稿状态的考试（未发布 且 尚未结束）
    if exam.is_published:
        return JsonResponse({
            'error': '只能删除草稿状态的考试',
            'detail': '已发布的考试请先取消发布后再删除',
        }, status=400)
    
    student_count = StudentExamRecord.objects.filter(exam=exam).count()
    
    # 删除关联的考试题目记录
    ExamQuestion.objects.filter(exam=exam).delete()
    
    # 删除考试
    exam.delete()
    
    return JsonResponse({
        'status': 'success',
        'message': '考试已删除',
        'deleted_students': student_count
    })

@login_required
def exam_students_api(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id, created_by=request.user)
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    
    records = StudentExamRecord.objects.filter(exam=exam, student__is_superuser=False).select_related('student')
    
    students_data = []
    for record in records:
        student_id = ''
        class_name = ''
        try:
            profile = StudentProfile.objects.get(user=record.student)
            student_id = profile.student_id
            class_name = profile.class_name
        except StudentProfile.DoesNotExist:
            pass
        
        students_data.append({
            'record_id': record.id,
            'student_id': student_id,
            'student_name': record.student.username,
            'class_name': class_name,
            'is_started': record.start_time is not None,
            'is_finished': record.is_finished,
            'is_graded': record.reviewed_at is not None,
            'score': record.score,
            'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M') if record.submit_time else None,
        })
    
    return JsonResponse({
        'exam_title': exam.title,
        'students': students_data,
        'total': len(students_data),
    })

@login_required
def grade_detail_api(request, record_id):
    try:
        record = StudentExamRecord.objects.get(id=record_id)
    except StudentExamRecord.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    if record.exam.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    exam = record.exam
    student_answers = record.answers or {}
    
    auto_score = 0
    questions_data = []
    exam_questions = ExamQuestion.objects.filter(exam=exam).order_by('order')
    
    for eq in exam_questions:
        try:
            question = Question.objects.get(id=eq.question_id)
            options = {}
            if question.type in ['single', 'multiple']:
                if isinstance(question.options, dict):
                    options = question.options
                else:
                    options = {}
            
            user_answer = student_answers.get(str(question.id), '')
            if isinstance(user_answer, list):
                user_answer = ','.join(sorted(user_answer))
            
            is_auto = question.type in ('single', 'multiple', 'judge', 'fill')
            if is_auto:
                correct_answer = str(question.answer).strip()
                user_answer_str = str(user_answer).strip()
                
                if question.type == 'multiple':
                    user_set = set(user_answer_str.upper().replace(',', ''))
                    correct_set = set(correct_answer.upper().replace(',', ''))
                    if user_set == correct_set:
                        auto_score += eq.score
                else:
                    if user_answer_str.lower() == correct_answer.lower():
                        auto_score += eq.score
            
            questions_data.append({
                'id': question.id,
                'type': question.type,
                'content': question.content,
                'options': options,
                'answer': question.answer,
                'score': eq.score,
            })
        except Question.DoesNotExist:
            continue
    
    return JsonResponse({
        'record_id': record.id,
        'exam_id': exam.id,
        'exam_title': exam.title,
        'total_score': exam.total_score,
        'auto_score': auto_score,
        'student_name': record.student.username,
        'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M') if record.submit_time else None,
        'score': record.score,
        'reviewed_at': record.reviewed_at.strftime('%Y-%m-%d %H:%M') if record.reviewed_at else None,
        'questions': questions_data,
        'student_answers': student_answers,
        'essay_scores': record.answers.get('_essay_scores', {}) if record.answers else {},
    })

@login_required
@csrf_exempt
def grade_submit_api(request, record_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        record = StudentExamRecord.objects.get(id=record_id)
    except StudentExamRecord.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    if record.exam.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    essay_scores = data.get('essay_scores', {})
    
    exam = record.exam
    
    for question_id_str, score in essay_scores.items():
        try:
            q_id = int(question_id_str)
            eq = ExamQuestion.objects.get(exam=exam, question_id=q_id)
            if int(score) > eq.score:
                return JsonResponse({
                    'error': f'题目 {q_id} 的评分 {score} 超过最高分 {eq.score}'
                }, status=400)
        except (ValueError, ExamQuestion.DoesNotExist):
            continue
    
    if record.answers is None:
        record.answers = {}
    record.answers['_essay_scores'] = essay_scores
    
    auto_score = 0
    
    exam_questions = ExamQuestion.objects.filter(exam=exam)
    for eq in exam_questions:
        try:
            question = Question.objects.get(id=eq.question_id)
            if question.type in ['single', 'multiple', 'judge', 'fill']:
                student_answer = record.answers.get(str(question.id), '')
                if isinstance(student_answer, list):
                    student_answer = ','.join(sorted(student_answer))
                student_answer = str(student_answer).strip()
                correct_answer = str(question.answer).strip()
                
                if question.type == 'multiple':
                    student_set = set(student_answer.upper().replace(',', ''))
                    correct_set = set(correct_answer.upper().replace(',', ''))
                    if student_set == correct_set:
                        auto_score += eq.score
                else:
                    if student_answer.lower() == correct_answer.lower():
                        auto_score += eq.score
        except Question.DoesNotExist:
            continue
    
    essay_total = 0
    for score in essay_scores.values():
        essay_total += int(score)
    
    record.score = auto_score + essay_total
    record.reviewed_at = timezone.now()
    record.save()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Grading completed',
        'total_score': record.score,
    })

@login_required
@csrf_exempt
def import_questions_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        questions_data = data.get('questions', [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    valid_types = ['single', 'multiple', 'judge', 'fill', 'essay', 'discussion']
    
    imported_count = 0
    failed_count = 0
    errors = []
    
    for idx, q_data in enumerate(questions_data):
        row_number = idx + 1
        
        # 验证题型
        q_type = q_data.get('type', '').strip()
        if not q_type:
            errors.append(f'第{row_number}行：题型不能为空')
            failed_count += 1
            continue
        
        if q_type not in valid_types:
            errors.append(f'第{row_number}行：无效题型 "{q_type}"，支持的题型：{", ".join(valid_types)}')
            failed_count += 1
            continue
        
        # 验证题目内容
        content = q_data.get('content', '').strip()
        if not content:
            errors.append(f'第{row_number}行：题目内容不能为空')
            failed_count += 1
            continue
        
        # 验证答案
        answer = q_data.get('answer', '').strip()
        if not answer:
            errors.append(f'第{row_number}行：答案不能为空')
            failed_count += 1
            continue
        
        # 验证分值
        score = q_data.get('score', 5)
        try:
            score = int(score)
            if score < 1 or score > 100:
                errors.append(f'第{row_number}行：分值必须在1-100之间')
                failed_count += 1
                continue
        except ValueError:
            errors.append(f'第{row_number}行：分值必须是数字')
            failed_count += 1
            continue
        
        # 验证难度
        difficulty = q_data.get('difficulty', 1)
        try:
            difficulty = int(difficulty)
            if difficulty < 1 or difficulty > 5:
                errors.append(f'第{row_number}行：难度必须在1-5之间')
                failed_count += 1
                continue
        except ValueError:
            errors.append(f'第{row_number}行：难度必须是数字')
            failed_count += 1
            continue
        
        # 验证选项（单选/多选）
        options = ''
        if q_type in ['single', 'multiple']:
            q_options = q_data.get('options', '')
            if not q_options:
                errors.append(f'第{row_number}行：单选/多选题必须有选项')
                failed_count += 1
                continue
            options = q_options
        
        # 验证判断题答案
        if q_type == 'judge' and answer not in ['True', 'False', 'true', 'false', 'T', 'F']:
            errors.append(f'第{row_number}行：判断题答案必须是 True 或 False')
            failed_count += 1
            continue
        
        # 创建题目
        Question.objects.create(
            type=q_type,
            content=content,
            options=options,
            answer=answer,
            score=score,
            analysis=q_data.get('analysis', ''),
            difficulty=difficulty,
            chapter=q_data.get('chapter', ''),
            knowledge_point=q_data.get('knowledge_point', ''),
            created_by=request.user,
        )
        imported_count += 1
    
    result = {
        'status': 'success' if failed_count == 0 else 'partial',
        'imported_count': imported_count,
        'failed_count': failed_count,
    }
    
    if errors:
        result['errors'] = errors[:20]
        if len(errors) > 20:
            result['errors'].append(f'... 还有 {len(errors) - 20} 条错误')
    
    return JsonResponse(result)


@login_required
def teacher_students_api(request):
    teacher = request.user
    
    students = StudentProfile.objects.filter(teacher=teacher, user__is_superuser=False)
    
    students_data = []
    for student in students:
        exam_count = StudentExamRecord.objects.filter(
            student=student.user, 
            exam__created_by=teacher,
            is_finished=True
        ).count()
        
        students_data.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.user.username,
            'email': student.user.email,
            'class_name': student.class_name,
            'major': student.major,
            'phone': student.phone,
            'exam_count': exam_count,
            'created_at': student.user.date_joined.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse(students_data, safe=False)


@login_required
def student_exams_api(request, student_id):
    teacher = request.user
    try:
        student = StudentProfile.objects.get(id=student_id, teacher=teacher)
    except StudentProfile.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

    records = StudentExamRecord.objects.filter(
        student=student.user,
        exam__created_by=teacher,
        is_finished=True
    ).select_related('exam').order_by('-submit_time')

    exams_data = []
    for record in records:
        is_graded = record.score is not None
        if record.is_finished:
            if is_graded:
                status = 'graded'
            else:
                status = 'finished'
        else:
            status = 'ongoing'
        exams_data.append({
            'record_id': record.id,
            'exam_id': record.exam.id,
            'title': record.exam.title,
            'total_score': record.exam.total_score,
            'score': record.score or 0,
            'status': status,
            'is_graded': is_graded,
            'submit_time': record.submit_time.strftime('%Y-%m-%d %H:%M') if record.submit_time else None,
        })

    return JsonResponse({
        'student_name': student.user.username,
        'student_id': student.student_id,
        'exams': exams_data,
    })


@login_required
def exam_result_api(request, record_id):
    try:
        record = StudentExamRecord.objects.get(id=record_id, exam__created_by=request.user)
    except StudentExamRecord.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    exam = record.exam
    
    question_results = []
    for question, score, _ in get_exam_questions(exam):
        user_answer = record.answers.get(str(question.id), '')
        if isinstance(user_answer, list):
            user_answer = ','.join(sorted(user_answer))
        options = get_options_dict_from_question(question)
        
        if question.type in ('essay', 'discussion'):
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
        })
    
    is_graded = record.reviewed_at is not None
    
    student_name = record.student.username
    try:
        profile = StudentProfile.objects.get(user=record.student)
        if profile.student_id:
            student_name = f"{profile.student_id} - {record.student.username}"
    except StudentProfile.DoesNotExist:
        pass
    
    auto_score = 0
    for question, score, _ in get_exam_questions(exam):
        if question.type in ('single', 'multiple', 'judge', 'fill'):
            user_answer = record.answers.get(str(question.id), '')
            if isinstance(user_answer, list):
                user_answer = ','.join(sorted(user_answer))
            if is_answer_correct(user_answer, question.answer, question.type):
                auto_score += score

    return JsonResponse({
        'student_name': student_name,
        'exam_id': exam.id,
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
            'auto_score': auto_score,
        },
        'questions': question_results,
    })

@login_required
def profile_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    teacher = request.user
    try:
        profile = TeacherProfile.objects.get(user=teacher)
        profile_data = {
            'username': teacher.username,
            'email': teacher.email,
            'teacher_id': profile.teacher_id,
            'department': profile.department,
            'title': profile.get_title_display() if profile.title else '',
            'phone': profile.phone,
            'office': profile.office,
            'avatar': request.build_absolute_uri(profile.avatar.url) if profile.avatar else None,
        }
    except TeacherProfile.DoesNotExist:
        profile_data = {
            'username': teacher.username,
            'email': teacher.email,
            'teacher_id': '',
            'department': '',
            'title': '',
            'phone': '',
            'office': '',
            'avatar': None,
        }

    return JsonResponse({'profile': profile_data})


@login_required
@csrf_exempt
def avatar_upload_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    profile, created = TeacherProfile.objects.get_or_create(user=request.user)
    if 'avatar' in request.FILES:
        profile.avatar = request.FILES['avatar']
        profile.save()
        return JsonResponse({
            'status': 'success',
            'avatar_url': request.build_absolute_uri(profile.avatar.url),
        })
    return JsonResponse({'error': 'No image file provided'}, status=400)


@login_required
@csrf_exempt
def reset_exam_record_api(request, record_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        record = StudentExamRecord.objects.select_related('exam').get(
            id=record_id, exam__created_by=request.user
        )
    except StudentExamRecord.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)

    with transaction.atomic():
        record.is_finished = False
        record.answers = {}
        record.score = None
        record.submit_time = None
        record.time_spent = 0
        record.teacher_comments = ''
        record.reviewed_at = None
        record.reviewed_by = None
        record.start_time = None
        record.save()

    return JsonResponse({
        'status': 'success',
        'message': '考试记录已重置，学生可以重新考试',
    })
