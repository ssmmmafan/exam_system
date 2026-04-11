from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import TeacherProfile, Question, QuestionTag
from exams.models import Exam, ExamQuestion
from students.models import StudentExamRecord
from django.utils import timezone
import datetime


class TeacherTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.client = Client()
        self.teacher_user = User.objects.create_user(username='teacher', password='testpassword', is_staff=True)
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            teacher_id='T12345',
            department='Computer Science',
            title='lecturer'
        )
        
        # 创建测试题目
        self.question = Question.objects.create(
            type='single',
            content='测试题目',
            options={'A': '选项A', 'B': '选项B'},
            answer='A',
            score=5,
            created_by=self.teacher_user
        )
        
        # 创建测试标签
        self.tag = QuestionTag.objects.create(name='测试标签')
        self.question.tags.add(self.tag)
        
        # 创建测试考试
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
        
        # 添加题目到考试
        self.exam_question = ExamQuestion.objects.create(
            exam=self.exam,
            question_id=self.question.id,
            order=1,
            score=5
        )
    
    def test_teacher_dashboard(self):
        """测试教师主页"""
        self.client.login(username='teacher', password='testpassword')
        response = self.client.get(reverse('teachers:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试考试')
    
    def test_question_creation(self):
        """测试题目创建"""
        self.client.login(username='teacher', password='testpassword')
        # 这里可以添加题目创建的测试
        # 由于没有题目创建的视图，这里只测试模型创建
        question = Question.objects.create(
            type='multiple',
            content='测试多选题',
            options={'A': '选项A', 'B': '选项B', 'C': '选项C'},
            answer='A,B',
            score=10,
            created_by=self.teacher_user
        )
        self.assertTrue(Question.objects.filter(id=question.id).exists())
    
    def test_exam_creation(self):
        """测试考试创建"""
        self.client.login(username='teacher', password='testpassword')
        # 这里可以添加考试创建的测试
        # 由于没有考试创建的视图，这里只测试模型创建
        exam = Exam.objects.create(
            title='新测试考试',
            description='新测试考试描述',
            duration=90,
            start_time=timezone.now() + datetime.timedelta(days=1),
            end_time=timezone.now() + datetime.timedelta(days=1, hours=1),
            total_score=100,
            is_published=False,
            created_by=self.teacher_user
        )
        self.assertTrue(Exam.objects.filter(id=exam.id).exists())
    
    def test_random_exam(self):
        """测试随机组卷"""
        self.client.login(username='teacher', password='testpassword')
        response = self.client.post(reverse('teachers:random_exam'), {
            'title': '随机组卷测试',
            'description': '随机组卷测试描述',
            'duration': 60,
            'start_time': timezone.now() + datetime.timedelta(days=1),
            'end_time': timezone.now() + datetime.timedelta(days=1, hours=1),
            'total_score': 100,
            'single_count': 1,
            'multiple_count': 0,
            'judge_count': 0,
            'essay_count': 0,
            'fill_count': 0,
            'discussion_count': 0
        })
        self.assertEqual(response.status_code, 302)  # 重定向到教师主页
        self.assertTrue(Exam.objects.filter(title='随机组卷测试').exists())
