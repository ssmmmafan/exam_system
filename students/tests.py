from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import StudentProfile, StudentExamRecord
from exams.models import Exam, ExamQuestion
from teachers.models import Question
from django.utils import timezone
import datetime


class StudentTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.student_profile = StudentProfile.objects.create(
            user=self.user,
            student_id='S12345',
            class_name='Class A',
            major='Computer Science'
        )
        
        # 创建测试题目
        self.question = Question.objects.create(
            type='single',
            content='测试题目',
            options={'A': '选项A', 'B': '选项B'},
            answer='A',
            score=5,
            created_by=self.user
        )
        
        # 创建测试考试
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
        
        # 添加题目到考试
        self.exam_question = ExamQuestion.objects.create(
            exam=self.exam,
            question_id=self.question.id,
            order=1,
            score=5
        )
    
    def test_student_register(self):
        """测试学生注册功能"""
        response = self.client.post(reverse('students:register'), {
            'username': 'newstudent',
            'password': 'password123',
            'password2': 'password123',
            'student_id': 'S67890',
            'email': 'newstudent@example.com',
            'class_name': 'Class B',
            'major': 'Mathematics'
        })
        self.assertEqual(response.status_code, 302)  # 重定向到登录页
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertTrue(StudentProfile.objects.filter(student_id='S67890').exists())
    
    def test_student_login(self):
        """测试学生登录功能"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # 重定向到学生主页
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_student_dashboard(self):
        """测试学生主页"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('students:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试考试')
    
    def test_exam_detail(self):
        """测试考试详情页"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('students:exam_detail', args=[self.exam.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试考试')
    
    def test_exam_taking(self):
        """测试考试进行页"""
        self.client.login(username='testuser', password='testpassword')
        # 先访问考试详情页创建记录
        self.client.get(reverse('students:exam_detail', args=[self.exam.id]))
        # 然后访问考试进行页
        response = self.client.get(reverse('students:exam_taking', args=[self.exam.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试题目')
    
    def test_submit_exam(self):
        """测试提交考试"""
        self.client.login(username='testuser', password='testpassword')
        # 先访问考试详情页创建记录
        self.client.get(reverse('students:exam_detail', args=[self.exam.id]))
        # 提交考试
        response = self.client.post(reverse('students:submit_exam', args=[self.exam.id]), {
            'question_1': 'A'
        })
        self.assertEqual(response.status_code, 302)  # 重定向到成绩页
        record = StudentExamRecord.objects.get(student=self.user, exam=self.exam)
        self.assertTrue(record.is_finished)
        self.assertEqual(record.score, 5)
