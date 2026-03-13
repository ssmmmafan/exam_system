from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),      # 登录页
    path('logout/', views.logout_view, name='logout'),   # 退出登录（新增）
    path('welcome/', views.welcome_view, name='welcome'), # 欢迎页
    path('', views.login_view),                           # 根路径跳转到登录页
]