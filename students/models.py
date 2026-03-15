from django.db import models
from django.contrib.auth.models import User
from exams.models import Exam  # 现在可以导入了


class StudentProfile(models.Model):
    """学生扩展信息（与User一对一关联）"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField('学号', max_length=20, unique=True)
    class_name = models.CharField('班级', max_length=50, blank=True)
    major = models.CharField('专业', max_length=100, blank=True)
    enrollment_year = models.IntegerField('入学年份', null=True, blank=True)
    phone = models.CharField('电话', max_length=11, blank=True)

    class Meta:
        db_table = 'student_profile'
        verbose_name = '学生信息'
        verbose_name_plural = '学生信息'

    def __str__(self):
        return f"{self.student_id} - {self.user.username}"


class StudentExamRecord(models.Model):
    """学生考试记录"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_exams')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_records')
    start_time = models.DateTimeField('开始时间', auto_now_add=True)
    submit_time = models.DateTimeField('提交时间', null=True, blank=True)
    answers = models.JSONField('答案', default=dict)  # 存储学生答案，格式：{"题目ID": "答案"}
    score = models.FloatField('得分', null=True, blank=True)
    is_finished = models.BooleanField('是否完成', default=False)
    time_spent = models.IntegerField('用时(秒)', default=0)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)

    class Meta:
        db_table = 'student_exam_record'
        verbose_name = '考试记录'
        verbose_name_plural = '考试记录'
        unique_together = ['student', 'exam']  # 一个学生一场考试只能有一条记录

        indexes = [
            models.Index(fields=['student', 'is_finished']),  # 添加索引
            models.Index(fields=['submit_time']),
        ]
    def __str__(self):
        status = "已完成" if self.is_finished else "进行中"
        return f"{self.student.username} - {self.exam.title} - {status}"