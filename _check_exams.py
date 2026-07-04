import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
import django; django.setup()

from exams.models import Exam
from django.utils import timezone

now = timezone.localtime()
print(f'当前时间: {now.strftime("%Y-%m-%d %H:%M")}')
print()
print('所有考试:')
for e in Exam.objects.all():
    start = timezone.localtime(e.start_time).strftime('%m-%d %H:%M')
    end = timezone.localtime(e.end_time).strftime('%m-%d %H:%M')
    print(f'  ID={e.id}, title={e.title}, start={start}, end={end}, published={e.is_published}')