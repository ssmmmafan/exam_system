from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),  # 👈 添加这一行
]