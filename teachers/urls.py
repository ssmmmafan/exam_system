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
]