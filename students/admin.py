from django.contrib import admin
from .models import StudentProfile, StudentExamRecord

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'class_name', 'major', 'teacher', 'enrollment_year')
    list_filter = ('teacher', 'class_name', 'major', 'enrollment_year')
    search_fields = ('student_id', 'user__username', 'class_name', 'major')
    raw_id_fields = ('user', 'teacher')

@admin.register(StudentExamRecord)
class StudentExamRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'is_finished', 'submit_time')
    list_filter = ('is_finished', 'exam', 'reviewed_at')
    search_fields = ('student__username', 'exam__title')
    raw_id_fields = ('student', 'exam', 'reviewed_by')