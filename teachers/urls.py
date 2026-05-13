from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pending/', views.pending_list, name='pending_list'),
    path('grade/<int:record_id>/', views.grade_essay, name='grade_essay'),
    path('ongoing/', views.ongoing_exams, name='ongoing_exams'),
    path('exam/<int:exam_id>/students/', views.exam_students, name='exam_students'),
    path('result/<int:record_id>/', views.student_result_detail, name='student_result_detail'),
    path('import/', views.import_questions, name='import_questions'),
    path('random-exam/', views.random_exam, name='random_exam'),
    path('exam/<int:exam_id>/publish/', views.publish_exam, name='publish_exam'),
    path('exam/<int:exam_id>/unpublish/', views.unpublish_exam, name='unpublish_exam'),
    path('questions/classification/', views.question_classification, name='question_classification'),
    path('questions/management/', views.question_management, name='question_management'),
    path('question/create/', views.create_question, name='create_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('questions/batch_delete/', views.batch_delete_questions, name='batch_delete_questions'),
    path('exam/create/', views.create_exam, name='create_exam'),
    path('exam/management/', views.exam_management, name='exam_management'),
    path('students/', views.my_students, name='my_students'),
]