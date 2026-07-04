from django.db import models
from django.contrib.auth.models import User
from exams.models import Exam


class ChatConversation(models.Model):
    """聊天会话模型"""
    TYPE_CHOICES = [
        ('private', '私聊'),
        ('exam', '考试聊天室'),
        ('class', '班级群聊'),
    ]
    
    type = models.CharField('会话类型', max_length=20, choices=TYPE_CHOICES, default='private')
    title = models.CharField('会话标题', max_length=200, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_conversations')
    participants = models.ManyToManyField(User, related_name='chat_conversations')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'chat_conversation'
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['exam']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        if self.title:
            return self.title
        elif self.exam:
            return f"{self.exam.title} - 聊天室"
        return f"会话 {self.id}"


class ChatMessage(models.Model):
    """聊天消息模型"""
    TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
        ('system', '系统通知'),
    ]
    
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField('消息内容')
    message_type = models.CharField('消息类型', max_length=20, choices=TYPE_CHOICES, default='text')
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'chat_message'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation']),
            models.Index(fields=['sender']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
