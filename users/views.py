from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):
    # 如果用户已登录，跳转到欢迎页
    if request.user.is_authenticated:
        return redirect('/welcome/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'欢迎回来，{username}！')
            return redirect('/welcome/')
        else:
            messages.error(request, '用户名或密码错误，请重试。')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, '您已成功退出登录！')
    return redirect('/login/')


def welcome_view(request):
    # 获取当前登录用户
    user = request.user

    # 判断用户角色
    role = "管理员" if user.is_staff else "学生"

    # 将数据传递给模板
    context = {
        'user': user,
        'role': role,
    }
    return render(request, 'users/welcome.html', context)