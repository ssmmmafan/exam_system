from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 限制 Django 后台仅超级管理员可登录
admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('users.api_urls')),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
