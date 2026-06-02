from django.urls import path
from . import api_views

app_name = 'teachers_api'

urlpatterns = [
    path('dashboard/', api_views.dashboard_api, name='dashboard_api'),
    path('questions/', api_views.question_list_api, name='question_list_api'),
    path('questions/stats/', api_views.question_stats_api, name='question_stats_api'),
    path('questions/batch/', api_views.batch_delete_questions_api, name='batch_delete_questions_api'),
    path('questions/create/', api_views.create_question_api, name='create_question_api'),
    path('questions/<int:question_id>/edit/', api_views.edit_question_api, name='edit_question_api'),
    path('questions/<int:question_id>/delete/', api_views.delete_question_api, name='delete_question_api'),
    path('questions/<int:question_id>/', api_views.question_detail_api, name='question_detail_api'),
    path('exams/', api_views.exam_list_api, name='exam_list_api'),
    path('exams/create/', api_views.create_exam_api, name='create_exam_api'),
    path('exams/random/', api_views.random_exam_api, name='random_exam_api'),
    path('exams/<int:exam_id>/publish/', api_views.publish_exam_api, name='publish_exam_api'),
    path('exams/<int:exam_id>/unpublish/', api_views.unpublish_exam_api, name='unpublish_exam_api'),
    path('exams/<int:exam_id>/delete/', api_views.delete_exam_api, name='delete_exam_api'),
    path('exams/<int:exam_id>/students/', api_views.exam_students_api, name='exam_students_api'),
    path('exams/<int:exam_id>/', api_views.exam_detail_api, name='exam_detail_api'),
    path('grade/<int:record_id>/', api_views.grade_detail_api, name='grade_detail_api'),
    path('grade/<int:record_id>/submit/', api_views.grade_submit_api, name='grade_submit_api'),
    path('questions/import/', api_views.import_questions_api, name='import_questions_api'),
    path('students/', api_views.teacher_students_api, name='teacher_students_api'),
    path('students/<int:student_id>/exams/', api_views.student_exams_api, name='student_exams_api'),
    path('result/<int:record_id>/', api_views.exam_result_api, name='exam_result_api'),
    path('profile/', api_views.profile_api, name='profile_api'),
    path('profile/avatar/', api_views.avatar_upload_api, name='avatar_upload'),
    path('record/<int:record_id>/reset/', api_views.reset_exam_record_api, name='reset_exam_record'),
]
