from django.urls import path
from . import api_views

app_name = 'students_api'

urlpatterns = [
    path('dashboard/', api_views.dashboard_api, name='dashboard_api'),
    path('exams/', api_views.exams_api, name='exams_api'),
    path('exam/<int:exam_id>/', api_views.exam_detail_api, name='exam_detail_api'),
    path('exam/<int:exam_id>/take/', api_views.exam_taking_api, name='exam_taking_api'),
    path('exam/<int:exam_id>/save/', api_views.save_answer_api, name='save_answer_api'),
    path('exam/<int:exam_id>/submit/', api_views.submit_exam_api, name='submit_exam_api'),
    path('results/', api_views.results_api, name='results_api'),
    path('result/<int:record_id>/', api_views.exam_result_api, name='exam_result_api'),
    path('wrong-questions/', api_views.wrong_questions_api, name='wrong_questions_api'),
    path('wrong-questions/delete/', api_views.delete_wrong_question_api, name='delete_wrong_question'),
    path('profile/', api_views.profile_api, name='profile_api'),
    path('profile/avatar/', api_views.avatar_upload_api, name='avatar_upload'),
]
