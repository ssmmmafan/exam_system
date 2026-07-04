from django.urls import path
from . import api_views

app_name = 'chat_api'

urlpatterns = [
    path('conversations/', api_views.conversation_list_api, name='conversation_list'),
    path('conversations/create/', api_views.create_conversation_api, name='create_conversation'),
    path('conversations/<int:conversation_id>/', api_views.conversation_detail_api, name='conversation_detail'),
    path('conversations/<int:conversation_id>/send/', api_views.send_message_api, name='send_message'),
    path('exams/<int:exam_id>/conversation/', api_views.ensure_exam_conversation_api, name='ensure_exam_conversation'),
]
