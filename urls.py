from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse


# 直接在同一个文件里定义登录视图
def login_view(request):
    # 如果用户已登录，跳转到admin
    if request.user.is_authenticated:
        return redirect('/admin/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 验证用户
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, '登录成功！')
            return redirect('/admin/')
        else:
            messages.error(request, '用户名或密码错误！')

    # 显示登录页面 - 直接在这里写HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>登录 - 在线考试系统</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .login-box {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                width: 350px;
            }
            h2 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 8px 0 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover {
                opacity: 0.9;
            }
            .message {
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
                text-align: center;
            }
            .success {
                background: #d4edda;
                color: #155724;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>📝 在线考试系统</h2>
    """

    # 添加消息显示
    if request.method == 'GET' and messages.get_messages(request):
        for message in messages.get_messages(request):
            html += f'<div class="message {message.tags}">{message}</div>'

    html += """
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="""" + request.COOKIES.get('csrftoken', '') + """">
                <label>用户名：</label>
                <input type="text" name="username" required>

                <label>密码：</label>
                <input type="password" name="password" required>

                <button type="submit">登录</button>
            </form>
        </div>
    </body>
    </html>
    """

    return HttpResponse(html)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view),  # 直接在这里添加login路径
]

print("✅ 主路由已加载，路径：", [str(p) for p in urlpatterns])