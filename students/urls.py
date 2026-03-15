from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/take/', views.exam_taking, name='exam_taking'),
    path('exam/<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
    path('result/<int:record_id>/', views.exam_result, name='exam_result'),
]