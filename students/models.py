from django.db import models
from django.contrib.auth.models import User
from exams.models import Exam


class StudentProfile(models.Model):
    """学生扩展信息（与User一对一关联）"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField('学号', max_length=20, unique=True)
    class_name = models.CharField('班级', max_length=50, blank=True)
    major = models.CharField('专业', max_length=100, blank=True)
    enrollment_year = models.IntegerField('入学年份', null=True, blank=True)
    phone = models.CharField('电话', max_length=11, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    deleted_wrong_ids = models.JSONField('已删除错题ID', default=list, blank=True)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students',
        verbose_name='负责教师'
    )

    class Meta:
        db_table = 'student_profile'
        verbose_name = '学生信息'
        verbose_name_plural = '学生信息'

    def __str__(self):
        return f"{self.student_id} - {self.user.username}"

    def clean(self):
        super().clean()
        if self.teacher:
            if not self.teacher.is_staff:
                from django.core.exceptions import ValidationError
                raise ValidationError({'teacher': '指定的教师必须具有教师权限（is_staff=True）'})
            if self.teacher.is_superuser:
                from django.core.exceptions import ValidationError
                raise ValidationError({'teacher': '不能将学生分配给超级管理员'})


class StudentExamRecord(models.Model):
    """学生考试记录"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_exams')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_records')
    start_time = models.DateTimeField('开始时间', null=True, blank=True)
    submit_time = models.DateTimeField('提交时间', null=True, blank=True)
    answers = models.JSONField('答案', default=dict)
    score = models.FloatField('得分', null=True, blank=True)
    is_finished = models.BooleanField('是否完成', default=False)
    time_spent = models.IntegerField('用时(秒)', default=0)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    teacher_comments = models.TextField('教师评语', blank=True, null=True)
    reviewed_at = models.DateTimeField('批改时间', null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_records'
    )
    class Meta:
        db_table = 'student_exam_record'
        verbose_name = '考试记录'
        verbose_name_plural = '考试记录'
        unique_together = ['student', 'exam']

        indexes = [
            models.Index(fields=['student', 'is_finished']),
            models.Index(fields=['submit_time']),
        ]
    def __str__(self):
        status = "已完成" if self.is_finished else "进行中"
        return f"{self.student.username} - {self.exam.title} - {status}"
