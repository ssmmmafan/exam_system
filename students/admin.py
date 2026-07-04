from django.contrib import admin
from .models import StudentProfile, StudentExamRecord

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'class_name', 'major', 'teacher', 'enrollment_year')
    list_filter = ('teacher', 'class_name', 'major', 'enrollment_year')
    search_fields = ('student_id', 'user__username', 'class_name', 'major')
    raw_id_fields = ('user',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'teacher':
            kwargs['queryset'] = db_field.related_model.objects.filter(is_staff=True, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.teacher:
            if not obj.teacher.is_staff:
                from django.core.exceptions import ValidationError
                raise ValidationError('指定的教师必须具有教师权限（is_staff=True）')
            if obj.teacher.is_superuser:
                from django.core.exceptions import ValidationError
                raise ValidationError('不能将学生分配给超级管理员')
        super().save_model(request, obj, form, change)

@admin.register(StudentExamRecord)
class StudentExamRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'is_finished', 'submit_time')
    list_filter = ('is_finished', 'exam', 'reviewed_at')
    search_fields = ('student__username', 'exam__title')
    raw_id_fields = ('student', 'exam', 'reviewed_by')
