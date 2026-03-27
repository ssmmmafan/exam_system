from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Exam, ExamQuestion
from teachers.models import Question


@staff_member_required
def select_questions(request, exam_id):
    """为考试选题的独立页面"""
    exam = Exam.objects.get(id=exam_id)

    # 获取已被选中的题目ID
    selected_ids = ExamQuestion.objects.filter(exam=exam).values_list('question_id', flat=True)

    # 获取未被选中的题目（当前教师创建的）
    available_questions = Question.objects.filter(
        created_by=request.user
    ).exclude(id__in=selected_ids)

    if request.method == 'POST':
        question_ids = request.POST.getlist('questions')
        for order, q_id in enumerate(question_ids, start=1):
            ExamQuestion.objects.create(
                exam=exam,
                question_id=q_id,
                order=order,
                score=Question.objects.get(id=q_id).score
            )
        messages.success(request, f'成功添加 {len(question_ids)} 道题目')
        return redirect('/admin/exams/exam/')

    context = {
        'exam': exam,
        'questions': available_questions,
    }
    return render(request, 'exams/select_questions.html', context)