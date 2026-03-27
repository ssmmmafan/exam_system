from django.contrib import admin
from .models import StudentProfile, StudentExamRecord

# 删除所有 UserAdmin 相关导入和代码
# 只保留学生档案和考试记录的注册

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'class_name', 'major')

@admin.register(StudentExamRecord)
class StudentExamRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'is_finished')