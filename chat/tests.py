from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
import json

from chat.models import ChatConversation, ChatMessage
from exams.models import Exam
from teachers.models import TeacherProfile


class ChatApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(username='chat_teacher', password='123456')
        self.student = User.objects.create_user(username='chat_student', password='123456')
        TeacherProfile.objects.create(
            user=self.teacher,
            teacher_id='T001',
            department='计算机',
        )
        now = timezone.now()
        self.exam = Exam.objects.create(
            title='聊天测试考试',
            duration=60,
            start_time=now - timedelta(days=1),
            end_time=now + timedelta(days=30),
            total_score=100,
            is_published=True,
            created_by=self.teacher,
        )

    def test_create_private_conversation(self):
        self.client.login(username='chat_teacher', password='123456')
        response = self.client.post(
            '/api/chat/conversations/create/',
            data=json.dumps({
                'type': 'private',
                'target_username': 'chat_student',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(
            ChatConversation.objects.filter(type='private').count(),
            1,
        )

    def test_private_conversation_is_reused(self):
        self.client.login(username='chat_teacher', password='123456')
        payload = json.dumps({'type': 'private', 'target_username': 'chat_student'})
        first = self.client.post('/api/chat/conversations/create/', data=payload, content_type='application/json')
        second = self.client.post('/api/chat/conversations/create/', data=payload, content_type='application/json')
        self.assertEqual(first.json()['conversation_id'], second.json()['conversation_id'])

    def test_exam_conversation_get_or_create(self):
        self.client.login(username='chat_teacher', password='123456')
        response = self.client.post(f'/api/chat/exams/{self.exam.id}/conversation/')
        self.assertEqual(response.status_code, 200)
        conversation_id = response.json()['conversation_id']

        self.client.login(username='chat_student', password='123456')
        response = self.client.post(f'/api/chat/exams/{self.exam.id}/conversation/')
        self.assertEqual(response.json()['conversation_id'], conversation_id)

    def test_send_message_and_mark_read(self):
        self.client.login(username='chat_teacher', password='123456')
        conversation_id = self.client.post(
            '/api/chat/conversations/create/',
            data=json.dumps({'type': 'private', 'target_username': 'chat_student'}),
            content_type='application/json',
        ).json()['conversation_id']

        send_response = self.client.post(
            f'/api/chat/conversations/{conversation_id}/send/',
            data=json.dumps({'content': '你好，同学'}),
            content_type='application/json',
        )
        self.assertTrue(send_response.json()['success'])
        self.assertEqual(ChatMessage.objects.count(), 1)

        self.client.login(username='chat_student', password='123456')
        detail_response = self.client.get(f'/api/chat/conversations/{conversation_id}/')
        self.assertTrue(detail_response.json()['success'])
        self.assertEqual(len(detail_response.json()['messages']), 1)
        self.assertTrue(ChatMessage.objects.filter(is_read=True).exists())

    def test_broadcast_helper_does_not_raise(self):
        from chat.broadcast import broadcast_new_message

        self.client.login(username='chat_teacher', password='123456')
        conversation_id = self.client.post(
            '/api/chat/conversations/create/',
            data=json.dumps({'type': 'private', 'target_username': 'chat_student'}),
            content_type='application/json',
        ).json()['conversation_id']

        message = ChatMessage.objects.create(
            conversation_id=conversation_id,
            sender=self.teacher,
            content='广播测试',
        )
        conversation = ChatConversation.objects.get(id=conversation_id)

        broadcast_new_message(
            conversation_id,
            {
                'id': message.id,
                'content': message.content,
                'type': message.message_type,
                'sender_id': message.sender_id,
                'sender_username': message.sender.username,
                'is_read': message.is_read,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            },
            {
                'id': conversation.id,
                'last_message': message.content,
                'last_time': conversation.updated_at.strftime('%Y-%m-%d %H:%M'),
            },
        )
