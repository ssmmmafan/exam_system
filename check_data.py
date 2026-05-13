from django.contrib.auth.models import User
from students.models import StudentProfile
from exams.models import Exam

print('=== Users ===')
for user in User.objects.all():
    print(f'  {user.username} (ID: {user.id}) - Staff: {user.is_staff}')

print('\n=== Student Profiles ===')
for sp in StudentProfile.objects.all():
    teacher_name = sp.teacher.username if sp.teacher else 'None'
    print(f'  {sp.user.username} (ID: {sp.user.id}) - Teacher: {teacher_name}')

print('\n=== Published Exams ===')
for exam in Exam.objects.filter(is_published=True):
    print(f'  {exam.title} (ID: {exam.id}) - Created by: {exam.created_by.username}')
    print(f'    Start: {exam.start_time}')
    print(f'    End: {exam.end_time}')
