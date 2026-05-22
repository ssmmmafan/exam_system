from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import TeacherProfile, Question, QuestionTag
from exams.models import Exam, ExamQuestion
from students.models import StudentExamRecord
from django.utils import timezone
import datetime
import json


class TeacherTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.teacher_user = User.objects.create_user(username='teacher', password='testpassword', is_staff=True)
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            teacher_id='T12345',
            department='Computer Science',
            title='lecturer'
        )
        
        self.question = Question.objects.create(
            type='single',
            content='测试题目',
            options={'A': '选项A', 'B': '选项B'},
            answer='A',
            score=5,
            created_by=self.teacher_user
        )
        
        self.tag = QuestionTag.objects.create(name='测试标签')
        self.question.tags.add(self.tag)
        
        self.exam = Exam.objects.create(
            title='测试考试',
            description='测试考试描述',
            duration=60,
            start_time=timezone.now() - datetime.timedelta(hours=1),
            end_time=timezone.now() + datetime.timedelta(hours=1),
            total_score=100,
            is_published=True,
            created_by=self.teacher_user
        )
        
        self.exam_question = ExamQuestion.objects.create(
            exam=self.exam,
            question_id=self.question.id,
            order=1,
            score=5
        )
    
    def test_teacher_dashboard_api(self):
        """测试教师仪表板API"""
        self.client.login(username='teacher', password='testpassword')
        response = self.client.get('/api/teacher/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_question_creation_api(self):
        """测试题目创建API"""
        self.client.login(username='teacher', password='testpassword')
        response = self.client.post(
            '/api/teacher/questions/',
            json.dumps({
                'type': 'multiple',
                'content': '测试多选题',
                'options': {'A': '选项A', 'B': '选项B', 'C': '选项C'},
                'answer': 'A,B',
                'score': 10
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
    
    def test_exam_creation_api(self):
        """测试考试创建API"""
        self.client.login(username='teacher', password='testpassword')
        start_time = (timezone.now() + datetime.timedelta(days=1)).isoformat()
        end_time = (timezone.now() + datetime.timedelta(days=1, hours=1)).isoformat()
        response = self.client.post(
            '/api/teacher/exams/create/',
            json.dumps({
                'title': '新测试考试',
                'description': '新测试考试描述',
                'duration': 90,
                'start_time': start_time,
                'end_time': end_time,
                'question_ids': [self.question.id]
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
    
    def test_random_exam_api(self):
        """测试随机组卷API"""
        self.client.login(username='teacher', password='testpassword')
        start_time = (timezone.now() + datetime.timedelta(days=1)).isoformat()
        end_time = (timezone.now() + datetime.timedelta(days=1, hours=1)).isoformat()
        response = self.client.post(
            '/api/teacher/exams/random/',
            json.dumps({
                'title': '随机组卷测试',
                'description': '随机组卷测试描述',
                'duration': 60,
                'start_time': start_time,
                'end_time': end_time,
                'question_spec': {'single': 1},
                'min_difficulty': 1,
                'max_difficulty': 5
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')