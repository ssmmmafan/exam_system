from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):
    # 如果用户已登录，根据角色跳转到不同页面
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')  # 管理员跳转到后台
        else:
            return redirect('/students/dashboard/')  # 学生跳转到学生主页

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'欢迎回来，{username}！')
            # 登录成功后根据角色跳转
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('/students/dashboard/')
        else:
            messages.error(request, '用户名或密码错误，请重试。')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, '您已成功退出登录！')
    return redirect('/login/')