from django.contrib import admin
from .models import Exam, ExamQuestion


class ExamQuestionInline(admin.TabularInline):
    """考试题目内联管理"""
    model = ExamQuestion
    extra = 1
    verbose_name = '考试题目'
    verbose_name_plural = '考试题目'

    # 只保留可编辑的字段，移除 raw_id_fields
    fields = ('question_id', 'order', 'score')
    # 不需要 raw_id_fields，因为 question_id 不是外键


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """考试管理"""
    list_display = ('id', 'title', 'created_by', 'start_time', 'end_time', 'is_published', 'created_at')
    list_filter = ('is_published', 'start_time', 'created_by')
    search_fields = ('title', 'description')
    raw_id_fields = ('created_by',)  # 这是外键，可以保留
    date_hierarchy = 'start_time'
    inlines = [ExamQuestionInline]

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'duration', 'total_score')
        }),
        ('时间设置', {
            'fields': ('start_time', 'end_time'),
            'classes': ('wide',)
        }),
        ('发布状态', {
            'fields': ('is_published', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """自动设置创建者"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    """考试题目关联管理"""
    list_display = ('id', 'exam', 'question_id', 'order', 'score')
    list_filter = ('exam',)
    search_fields = ('exam__title',)
    # 移除 raw_id_fields