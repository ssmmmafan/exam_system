from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.cache import cache
from django.http import HttpResponse
from .models import TeacherProfile, Question, QuestionTag
from exams.models import Exam, ExamQuestion
from students.models import StudentExamRecord, StudentProfile

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

    # 清除缓存，确保获取最新数据
    cache_key = f'teacher_dashboard_{request.user.id}'
    cache.delete(cache_key)
    
    # 执行查询
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

    import json
    
    # 获取进行中的考试详情
    ongoing_exams_list = Exam.objects.filter(
        created_by=request.user,
        start_time__lte=now,
        end_time__gte=now
    ).only('id', 'title', 'end_time')
    
    ongoing_exams_data = []
    for exam in ongoing_exams_list:
        student_count = StudentExamRecord.objects.filter(exam=exam).count()
        ongoing_exams_data.append({
            'id': exam.id,
            'title': exam.title,
            'end_time': exam.end_time.isoformat(),
            'student_count': student_count,
        })
    
    # 获取待批改列表
    pending_records = StudentExamRecord.objects.filter(
        exam__created_by=request.user,
        is_finished=True,
        score__isnull=True
    ).select_related('student', 'exam').order_by('submit_time')[:5]
    
    pending_exams_data = []
    for record in pending_records:
        pending_exams_data.append({
            'id': record.id,
            'exam_title': record.exam.title,
            'student_name': record.student.username,
        })
    
    # 获取学生总数
    total_students = StudentProfile.objects.count()
    
    stats_data = {
        'total_questions': total_questions,
        'total_exams': total_exams,
        'ongoing_exams': ongoing_exams,
        'pending_grading': pending_grading,
        'total_students': total_students,
    }
    
    recent_questions_data = []
    for q in recent_questions:
        recent_questions_data.append({
            'id': q.id,
            'type': q.type,
            'content': q.content[:50] + '...' if len(q.content) > 50 else q.content,
        })
    
    context = {
        'total_questions': total_questions,
        'total_exams': total_exams,
        'ongoing_exams': ongoing_exams,
        'pending_grading': pending_grading,
        'recent_exams': recent_exams,
        'recent_questions': recent_questions,
        'stats_json': json.dumps(stats_data),
        'ongoing_exams_json': json.dumps(ongoing_exams_data),
        'pending_exams_json': json.dumps(pending_exams_data),
        'recent_questions_json': json.dumps(recent_questions_data),
    }
    
    use_vue = request.session.get('use_vue', True)
    vue_param = request.GET.get('vue')
    if vue_param is not None:
        use_vue = vue_param.lower() == 'true'
        request.session['use_vue'] = use_vue
    
    if use_vue:
        return render(request, 'teachers/dashboard_vue.html', context)
    
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

    # 获取教师的所有学生
    teacher_students = StudentProfile.objects.filter(teacher=request.user).select_related('user')
    student_users = [sp.user for sp in teacher_students]

    # 获取所有学生的考试记录
    all_records = {}
    existing_records = StudentExamRecord.objects.filter(
        exam=exam,
        student__in=student_users
    ).select_related('student')

    # 构建记录字典
    for record in existing_records:
        all_records[record.student.id] = record

    # 为每个学生创建记录（如果不存在）
    records = []
    for sp in teacher_students:
        student = sp.user
        if student.id not in all_records:
            # 创建未参加的记录
            record = StudentExamRecord(
                student=student,
                exam=exam,
                is_finished=False
            )
            record.status = '未参加'
            record.status_badge = 'secondary'
            record.can_grade = False
        else:
            record = all_records[student.id]
            # 为已有记录添加状态
            if record.is_finished:
                if record.score is None:
                    record.status = '待批改'
                    record.status_badge = 'warning'
                    record.can_grade = True
                else:
                    record.status = '已批改'
                    record.status_badge = 'success'
                    record.can_grade = False
            else:
                record.status = '进行中'
                record.status_badge = 'info'
                record.can_grade = False
        records.append(record)

    # 统计
    total_students = len(records)
    completed_students = sum(1 for r in records if getattr(r, 'is_finished', False))
    scored_records = [r for r in records if getattr(r, 'score', None) is not None]
    avg_score = sum(r.score for r in scored_records) / len(scored_records) if scored_records else 0

    # 按状态排序：未参加 -> 进行中 -> 待批改 -> 已批改
    status_order = {'未参加': 0, '进行中': 1, '待批改': 2, '已批改': 3}
    records.sort(key=lambda r: status_order.get(r.status, 999))

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
                
                # 处理题目内容：去除"学科第X题："前缀
                content = str(row['content'])
                import re
                content = re.sub(r'^[\\u4e00-\\u9fa5]+第\\d+题：', '', content)
                
                # 处理选项：单选题和多选题需要选项
                options = None
                question_type = str(row['type']).strip().lower()
                if 'options' in row and pd.notna(row['options']):
                    options_str = str(row['options']).strip()
                    if options_str:
                        try:
                            import json
                            # 处理CSV转义的双引号
                            options_str = options_str.replace('""', '"')
                            options = json.loads(options_str)
                        except:
                            # 如果JSON解析失败，尝试按分号分隔
                            options = {}
                            parts = options_str.split(';')
                            for i, part in enumerate(parts):
                                key = chr(ord('A') + i)
                                options[key] = part.strip()
                
                # 处理章节和知识点
                chapter = str(row['chapter']).strip() if 'chapter' in row and pd.notna(row['chapter']) else ''
                knowledge_point = str(row['knowledge_point']).strip() if 'knowledge_point' in row and pd.notna(row['knowledge_point']) else ''
                
                # 处理难度
                difficulty = int(row['difficulty']) if 'difficulty' in row and pd.notna(row['difficulty']) else 3
                
                # 处理解析
                analysis = str(row['analysis']).strip() if 'analysis' in row and pd.notna(row['analysis']) else ''

                # 创建题目
                question = Question.objects.create(
                    type=question_type,
                    content=content,
                    options=options if options else {},
                    answer=str(row['answer']),
                    score=int(row['score']),
                    difficulty=difficulty,
                    chapter=chapter,
                    knowledge_point=knowledge_point,
                    analysis=analysis,
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
        
        # 创建考试（先不设置总分，后面计算）
        exam = Exam.objects.create(
            title=title,
            description=description,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
            is_published=False,
            random_questions=random_questions,
            random_options=random_options,
            enable_monitoring=enable_monitoring,
            created_by=request.user
        )
        
        # 随机选择题目并计算总分
        total_score = 0
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
                    total_score += question.score
                    order += 1
        
        # 更新考试总分
        exam.total_score = total_score
        exam.save()
        
        # 清除教师仪表板缓存
        cache_key = f'teacher_dashboard_{request.user.id}'
        cache.delete(cache_key)
        
        messages.success(request, f'随机组卷成功！总分 {total_score}')
        return redirect('teachers:dashboard')
    
    # 获取题型列表
    question_types = Question.QUESTION_TYPES
    
    context = {
        'question_types': question_types,
    }
    return render(request, 'teachers/random_exam.html', context)


@login_required
def publish_exam(request, exam_id):
    """发布考试"""
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    exam.is_published = True
    exam.save()
    # 清除教师仪表板缓存
    cache_key = f'teacher_dashboard_{request.user.id}'
    cache.delete(cache_key)
    messages.success(request, '考试已成功发布')
    return redirect('teachers:dashboard')


@login_required
def unpublish_exam(request, exam_id):
    """取消发布考试"""
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    exam.is_published = False
    exam.save()
    # 清除教师仪表板缓存
    cache_key = f'teacher_dashboard_{request.user.id}'
    cache.delete(cache_key)
    messages.success(request, '考试已取消发布')
    return redirect('teachers:dashboard')


@login_required
def question_classification(request):
    """按题型分类显示题目"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')

    question_type = request.GET.get('type', 'all')
    question_types = Question.QUESTION_TYPES
    questions_query = Question.objects.filter(created_by=request.user)
    
    if question_type != 'all':
        questions_query = questions_query.filter(type=question_type)
    
    questions_by_type = {}
    for qtype, type_name in question_types:
        questions_by_type[qtype] = {
            'name': type_name,
            'count': questions_query.filter(type=qtype).count(),
            'questions': questions_query.filter(type=qtype).order_by('-created_at')[:10]
        }
    
    if question_type != 'all':
        current_type_questions = questions_query.order_by('-created_at')
        paginator = Paginator(current_type_questions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    
    total_questions = questions_query.count()
    type_distribution = [
        {'type': qtype, 'name': type_name, 'count': questions_by_type[qtype]['count']}
        for qtype, type_name in question_types
    ]
    
    context = {
        'question_types': question_types,
        'questions_by_type': questions_by_type,
        'current_type': question_type,
        'page_obj': page_obj,
        'total_questions': total_questions,
        'type_distribution': type_distribution,
    }
    
    return render(request, 'teachers/question_classification.html', context)


@login_required
def my_students(request):
    """查看我负责的学生"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')
    
    students = StudentProfile.objects.filter(teacher=request.user).select_related('user').order_by('-id')
    
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    total_students = students.count()
    
    context = {
        'page_obj': page_obj,
        'total_students': total_students,
    }
    
    return render(request, 'teachers/my_students.html', context)


@login_required
def exam_management(request):
    """考试管理页面 - 整合所有考试相关功能"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')
    
    now = timezone.now()
    
    # 所有考试
    all_exams = Exam.objects.filter(created_by=request.user).order_by('-created_at')
    
    # 进行中的考试
    ongoing_exams = Exam.objects.filter(
        created_by=request.user,
        start_time__lte=now,
        end_time__gte=now,
        is_published=True
    ).order_by('start_time')
    
    # 即将开始的考试
    upcoming_exams = Exam.objects.filter(
        created_by=request.user,
        start_time__gt=now,
        is_published=True
    ).order_by('start_time')
    
    # 已结束的考试
    ended_exams = Exam.objects.filter(
        created_by=request.user,
        end_time__lt=now,
        is_published=True
    ).order_by('-end_time')
    
    # 待批改的试卷
    pending_records = StudentExamRecord.objects.filter(
        exam__created_by=request.user,
        is_finished=True,
        score__isnull=True
    ).select_related('student', 'exam').order_by('submit_time')
    
    context = {
        'all_exams': all_exams,
        'ongoing_exams': ongoing_exams,
        'upcoming_exams': upcoming_exams,
        'ended_exams': ended_exams,
        'pending_records': pending_records,
        'now': now,
    }
    
    return render(request, 'teachers/exam_management.html', context)


@login_required
def question_management(request):
    """试题管理主页面"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')
    
    # 获取URL参数
    question_type = request.GET.get('type', 'all')
    search = request.GET.get('search', '')
    difficulty = request.GET.get('difficulty', 'all')
    
    # 构建查询
    questions_query = Question.objects.filter(created_by=request.user)
    
    # 按类型筛选
    if question_type != 'all':
        questions_query = questions_query.filter(type=question_type)
    
    # 按难度筛选
    if difficulty != 'all' and difficulty.isdigit():
        questions_query = questions_query.filter(difficulty=int(difficulty))
    
    # 搜索
    if search:
        questions_query = questions_query.filter(
            Q(content__icontains=search) | 
            Q(knowledge_point__icontains=search)
        )
    
    # 分页
    paginator = Paginator(questions_query.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 统计数据
    total_questions = questions_query.count()
    type_stats = {}
    for qtype, type_name in Question.QUESTION_TYPES:
        type_stats[qtype] = {
            'name': type_name,
            'count': questions_query.filter(type=qtype).count()
        }
    
    context = {
        'page_obj': page_obj,
        'total_questions': total_questions,
        'question_types': Question.QUESTION_TYPES,
        'type_stats': type_stats,
        'current_type': question_type,
        'current_difficulty': difficulty,
        'search': search,
    }
    
    return render(request, 'teachers/question_management.html', context)


@login_required
def create_exam(request):
    """创建试卷（按分类选择试题）"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')
    
    if request.method == 'POST':
        # 处理表单提交
        title = request.POST.get('title')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        # 创建考试
        exam = Exam.objects.create(
            title=title,
            description=description,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
            created_by=request.user
        )
        
        # 处理题目选择
        total_score = 0
        question_order = 1
        
        # 遍历所有提交的题目ID和分值
        for key, value in request.POST.items():
            if key.startswith('question_') and '_score' not in key:
                question_id = key.split('_')[1]
                score_key = f'question_{question_id}_score'
                score = request.POST.get(score_key, 0)
                
                if score.isdigit():
                    score = int(score)
                    total_score += score
                    
                    # 添加题目到考试
                    ExamQuestion.objects.create(
                        exam=exam,
                        question_id=question_id,
                        order=question_order,
                        score=score
                    )
                    question_order += 1
        
        # 更新总分
        exam.total_score = total_score
        exam.save()
        
        # 清除教师仪表板缓存
        cache_key = f'teacher_dashboard_{request.user.id}'
        cache.delete(cache_key)
        
        messages.success(request, f'试卷 "{title}" 创建成功，共 {question_order-1} 道题目，总分 {total_score}')
        return redirect('teachers:dashboard')
    
    # GET请求：显示表单
    question_types = Question.QUESTION_TYPES
    
    # 获取搜索和筛选参数
    search = request.GET.get('search', '')
    difficulty = request.GET.get('difficulty', 'all')
    
    # 按题型获取题目（带分页）
    questions_by_type = {}
    for qtype, type_name in question_types:
        # 构建查询
        query = Question.objects.filter(
            created_by=request.user,
            type=qtype
        )
        
        # 搜索
        if search:
            query = query.filter(
                Q(content__icontains=search) | 
                Q(knowledge_point__icontains=search)
            )
        
        # 难度筛选
        if difficulty != 'all' and difficulty.isdigit():
            query = query.filter(difficulty=int(difficulty))
        
        # 分页
        paginator = Paginator(query.order_by('-created_at'), 20)
        page_number = request.GET.get(f'page_{qtype}')
        page_obj = paginator.get_page(page_number)
        
        questions_by_type[qtype] = {
            'name': type_name,
            'questions': page_obj,
            'paginator': paginator,
            'page_obj': page_obj
        }
    
    # 定义题型显示顺序（按考试常用顺序）
    exam_question_order = [
        {'type': 'single', 'name': '单选题'},
        {'type': 'multiple', 'name': '多选题'},
        {'type': 'judge', 'name': '判断题'},
        {'type': 'fill', 'name': '填空题'},
        {'type': 'essay', 'name': '简答题'},
        {'type': 'discussion', 'name': '论述题'}
    ]
    
    context = {
        'question_types': question_types,
        'questions_by_type': questions_by_type,
        'search': search,
        'difficulty': difficulty,
        'exam_question_order': exam_question_order,
    }
    
    return render(request, 'teachers/create_exam.html', context)


@login_required
def create_question(request):
    """创建试题"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')
    
    if request.method == 'POST':
        # 获取表单数据
        qtype = request.POST.get('type')
        content = request.POST.get('content')
        score = request.POST.get('score')
        difficulty = request.POST.get('difficulty')
        answer = request.POST.get('answer')
        analysis = request.POST.get('analysis')
        chapter = request.POST.get('chapter')
        knowledge_point = request.POST.get('knowledge_point')
        
        # 处理选项（JSON格式）
        options = {}
        if qtype in ['single', 'multiple']:
            # 收集选项
            for i, letter in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
                option_text = request.POST.get(f'option_{letter}')
                if option_text:
                    options[letter] = option_text
        
        # 验证数据
        if not all([qtype, content, score, difficulty, answer]):
            messages.error(request, '请填写完整的题目信息')
            return redirect('teachers:create_question')
        
        try:
            score = int(score)
            difficulty = int(difficulty)
        except ValueError:
            messages.error(request, '分值和难度必须是数字')
            return redirect('teachers:create_question')
        
        # 创建试题
        question = Question.objects.create(
            type=qtype,
            content=content,
            options=options if options else None,
            answer=answer,
            analysis=analysis,
            score=score,
            difficulty=difficulty,
            chapter=chapter,
            knowledge_point=knowledge_point,
            created_by=request.user
        )
        
        # 清除缓存
        cache_key = f'teacher_dashboard_{request.user.id}'
        cache.delete(cache_key)
        
        messages.success(request, f'试题创建成功！ID: {question.id}')
        return redirect('teachers:question_management')
    
    # GET请求：显示表单
    question_types = Question.QUESTION_TYPES
    
    context = {
        'question_types': question_types,
    }
    return render(request, 'teachers/create_question.html', context)


@login_required
def edit_question(request, question_id):
    """编辑试题"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')
    
    # 获取试题，确保是当前教师创建的
    question = get_object_or_404(Question, id=question_id, created_by=request.user)
    
    if request.method == 'POST':
        # 获取表单数据
        qtype = request.POST.get('type')
        content = request.POST.get('content')
        score = request.POST.get('score')
        difficulty = request.POST.get('difficulty')
        answer = request.POST.get('answer')
        analysis = request.POST.get('analysis')
        chapter = request.POST.get('chapter')
        knowledge_point = request.POST.get('knowledge_point')
        
        # 处理选项（JSON格式）
        options = {}
        if qtype in ['single', 'multiple']:
            # 收集选项
            for i, letter in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
                option_text = request.POST.get(f'option_{letter}')
                if option_text:
                    options[letter] = option_text
        
        # 验证数据
        if not all([qtype, content, score, difficulty, answer]):
            messages.error(request, '请填写完整的题目信息')
            return redirect('teachers:edit_question', question_id=question.id)
        
        try:
            score = int(score)
            difficulty = int(difficulty)
        except ValueError:
            messages.error(request, '分值和难度必须是数字')
            return redirect('teachers:edit_question', question_id=question.id)
        
        # 更新试题
        question.type = qtype
        question.content = content
        question.options = options if options else None
        question.answer = answer
        question.analysis = analysis
        question.score = score
        question.difficulty = difficulty
        question.chapter = chapter
        question.knowledge_point = knowledge_point
        question.save()
        
        # 清除缓存
        cache_key = f'teacher_dashboard_{request.user.id}'
        cache.delete(cache_key)
        
        messages.success(request, f'试题编辑成功！ID: {question.id}')
        return redirect('teachers:question_management')
    
    # GET请求：显示表单
    question_types = Question.QUESTION_TYPES
    
    context = {
        'question_types': question_types,
        'question': question,
        'is_edit': True,
    }
    return render(request, 'teachers/create_question.html', context)


@login_required
def delete_question(request, question_id):
    """删除试题"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')
    
    # 获取试题，确保是当前教师创建的
    question = get_object_or_404(Question, id=question_id, created_by=request.user)
    
    if request.method == 'POST':
        question.delete()
        
        # 清除相关缓存
        cache_key = f'teacher_dashboard_{request.user.id}'
        cache.delete(cache_key)
        
        messages.success(request, '试题删除成功')
        return redirect('teachers:question_management')
    
    return render(request, 'teachers/delete_question.html', {
        'question': question
    })


@login_required
def batch_delete_questions(request):
    """批量删除试题"""
    if not is_teacher(request.user):
        messages.error(request, '你没有权限访问')
        return redirect('/')
    
    if request.method == 'POST':
        # 获取逗号分隔的字符串并转换为列表
        question_ids_str = request.POST.get('question_ids', '')
        question_ids = [id.strip() for id in question_ids_str.split(',') if id.strip()]
        
        if question_ids:
            # 只删除当前用户创建的试题
            questions = Question.objects.filter(
                id__in=question_ids,
                created_by=request.user
            )
            deleted_count = questions.delete()[0]
            
            # 清除相关缓存
            cache_key = f'teacher_dashboard_{request.user.id}'
            cache.delete(cache_key)
            
            messages.success(request, f'成功删除 {deleted_count} 道试题')
        else:
            messages.warning(request, '请至少选择一道试题')
    
    return redirect('teachers:question_management')