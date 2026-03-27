from django.db import models
from django.contrib.auth.models import User


class TeacherProfile(models.Model):
    """教师扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    teacher_id = models.CharField('工号', max_length=20, unique=True)
    department = models.CharField('院系', max_length=100)
    title = models.CharField('职称', max_length=50, blank=True, choices=[
        ('assistant', '助教'),
        ('lecturer', '讲师'),
        ('associate', '副教授'),
        ('professor', '教授'),
    ])
    phone = models.CharField('电话', max_length=11, blank=True)
    office = models.CharField('办公室', max_length=100, blank=True)

    class Meta:
        db_table = 'teacher_profile'
        verbose_name = '教师信息'
        verbose_name_plural = '教师信息'
        # 添加索引
        indexes = [
            models.Index(fields=['teacher_id']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.teacher_id} - {self.user.username}"


class Question(models.Model):
    """试题库"""
    QUESTION_TYPES = (
        ('single', '单选题'),
        ('multiple', '多选题'),
        ('judge', '判断题'),
        ('essay', '简答题'),
    )
    DIFFICULTY_LEVELS = (
        (1, '简单'),
        (2, '较易'),
        (3, '中等'),
        (4, '较难'),
        (5, '困难'),
    )

    type = models.CharField('题型', max_length=20, choices=QUESTION_TYPES)
    content = models.TextField('题目内容')
    options = models.JSONField('选项', default=dict, help_text='单选题/多选题的选项，格式：{"A": "选项A", "B": "选项B"}')
    answer = models.TextField('正确答案', help_text='单选题存"A"，多选题存"A,B,C"，判断题存"对"或"错"')
    analysis = models.TextField('答案解析', blank=True)
    score = models.IntegerField('默认分值', default=5)
    difficulty = models.IntegerField('难度', choices=DIFFICULTY_LEVELS, default=3)
    chapter = models.CharField('所属章节', max_length=100, blank=True)
    knowledge_point = models.CharField('知识点', max_length=200, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_questions')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'question'
        verbose_name = '试题'
        verbose_name_plural = '试题'
        ordering = ['-created_at']
        # 添加索引
        indexes = [
            models.Index(fields=['created_by']),      # 按教师查询
            models.Index(fields=['type']),            # 按题型筛选
            models.Index(fields=['difficulty']),      # 按难度筛选
            models.Index(fields=['created_at']),      # 按时间排序
        ]

    def __str__(self):
        return f"[{self.get_type_display()}] {self.content[:50]}"