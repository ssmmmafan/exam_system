from django import forms
from django.contrib import admin
from .models import TeacherProfile, Question


class QuestionForm(forms.ModelForm):
    """试题动态表单"""

    class Meta:
        model = Question
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        question_type = self.data.get('type') or (self.instance.type if self.instance.pk else None)

        # 根据题型动态调整字段
        if question_type == 'single':
            self.fields['options'].help_text = '格式：{"A": "选项A", "B": "选项B", "C": "选项C"}'
            self.fields['answer'].help_text = '单选题：填写选项字母，如 A'
        elif question_type == 'multiple':
            self.fields['options'].help_text = '格式：{"A": "选项A", "B": "选项B", "C": "选项C"}'
            self.fields['answer'].help_text = '多选题：用逗号分隔选项字母，如 A,B'
        elif question_type == 'judge':
            self.fields['options'].widget = forms.HiddenInput()
            self.fields['options'].required = False
            self.fields['answer'].help_text = '判断题：填写"对"或"错"'
        elif question_type == 'essay':
            self.fields['options'].widget = forms.HiddenInput()
            self.fields['options'].required = False
            self.fields['answer'].help_text = '简答题：填写参考答案'
        else:
            # 默认显示
            self.fields['options'].help_text = '单选题/多选题请填写选项'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """试题管理"""
    form = QuestionForm
    list_display = ('id', 'type', 'short_content', 'difficulty', 'score', 'created_by', 'created_at')
    list_filter = ('type', 'difficulty', 'created_by')
    search_fields = ('content', 'knowledge_point')
    list_per_page = 20
    date_hierarchy = 'created_at'


    fieldsets = (
        ('基本信息', {
            'fields': ('type', 'content', 'score', 'difficulty')
        }),
        ('题目选项', {
            'fields': ('options',),
            'description': '单选题/多选题需要填写选项，判断题和简答题不需要'
        }),
        ('答案与解析', {
            'fields': ('answer', 'analysis'),
        }),
        ('分类信息', {
            'fields': ('chapter', 'knowledge_point', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    short_content.short_description = '题目内容'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)