from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('exam/<int:exam_id>/select/', views.select_questions, name='select_questions'),
]