from django.contrib import admin
from .models import ChatConversation, ChatMessage


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'title', 'created_at', 'updated_at']
    list_filter = ['type', 'created_at']
    search_fields = ['title']
    filter_horizontal = ['participants']
    date_hierarchy = 'created_at'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['content']
    date_hierarchy = 'created_at'
