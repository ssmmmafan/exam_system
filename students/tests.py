from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import StudentProfile, StudentExamRecord
from exams.models import Exam, ExamQuestion
from teachers.models import Question
from django.utils import timezone
import datetime
import json


class StudentTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.student_profile = StudentProfile.objects.create(
            user=self.user,
            student_id='S12345',
            class_name='Class A',
            major='Computer Science'
        )
        
        self.question = Question.objects.create(
            type='single',
            content='测试题目',
            options={'A': '选项A', 'B': '选项B'},
            answer='A',
            score=5,
            created_by=self.user
        )
        
        self.exam = Exam.objects.create(
            title='测试考试',
            description='测试考试描述',
            duration=60,
            start_time=timezone.now() - datetime.timedelta(hours=1),
            end_time=timezone.now() + datetime.timedelta(hours=1),
            total_score=100,
            is_published=True,
            created_by=self.user
        )
        
        self.exam_question = ExamQuestion.objects.create(
            exam=self.exam,
            question_id=self.question.id,
            order=1,
            score=5
        )
    
    def test_student_login_api(self):
        """测试学生登录API - 使用会话登录"""
        response = self.client.login(username='testuser', password='testpassword')
        self.assertTrue(response)
        
        response = self.client.get('/api/student/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_student_dashboard_api(self):
        """测试学生仪表板API"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/api/student/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_exam_list_api(self):
        """测试考试列表API"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/api/student/exams/')
        self.assertEqual(response.status_code, 200)
    
    def test_exam_detail_api(self):
        """测试考试详情API"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/api/student/exam/{self.exam.id}/')
        self.assertEqual(response.status_code, 200)
    
    def test_exam_taking_api(self):
        """测试考试进行API"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/api/student/exam/{self.exam.id}/take/')
        self.assertEqual(response.status_code, 200)
    
    def test_submit_exam_api(self):
        """测试提交考试API"""
        self.client.login(username='testuser', password='testpassword')
        self.client.get(f'/api/student/exam/{self.exam.id}/take/')
        response = self.client.post(
            f'/api/student/exam/{self.exam.id}/submit/',
            json.dumps({'answers': {str(self.question.id): 'A'}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')