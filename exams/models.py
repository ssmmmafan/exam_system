from django.db import models
from django.contrib.auth.models import User


class Exam(models.Model):
    """考试模型"""
    title = models.CharField('考试标题', max_length=200)
    description = models.TextField('考试描述', blank=True)
    duration = models.IntegerField('考试时长（分钟）')
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    total_score = models.IntegerField('总分', default=100)
    is_published = models.BooleanField('是否发布', default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'exam'
        verbose_name = '考试'
        verbose_name_plural = '考试'

    def __str__(self):
        return self.title


class ExamQuestion(models.Model):
    """考试题目关联表（用于组卷）"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_questions')
    question_id = models.IntegerField('题目ID')  # 暂时用ID，后续关联questions应用
    order = models.IntegerField('题目顺序')
    score = models.IntegerField('分值', default=5)

    class Meta:
        db_table = 'exam_question'
        ordering = ['order']
        unique_together = ['exam', 'order']  # 同一场考试题目顺序不能重复

    def __str__(self):
        return f"{self.exam.title} - 第{self.order}题"