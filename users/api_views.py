from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from students.models import StudentProfile
from teachers.models import TeacherProfile
import json

@csrf_exempt
def login_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'student')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        if user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': '超级用户请通过管理后台登录'
            }, status=403)
        
        login(request, user)
        
        is_student = StudentProfile.objects.filter(user=user).exists()
        is_teacher = TeacherProfile.objects.filter(user=user).exists()
        
        if is_student and role == 'student':
            user_role = 'student'
        elif is_teacher and role == 'teacher':
            user_role = 'teacher'
        else:
            return JsonResponse({'success': False, 'message': '角色不匹配'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message': '登录成功',
            'token': 'session_token_' + str(user.id),
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user_role,
                'realname': getattr(user, 'realname', '')
            }
        })
    else:
        return JsonResponse({'success': False, 'message': '用户名或密码错误'}, status=401)

@csrf_exempt  
def logout_api(request):
    logout(request)
    return JsonResponse({'success': True, 'message': '登出成功'})

@csrf_exempt
def change_password_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
    
    try:
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    
    if not old_password or not new_password:
        return JsonResponse({'success': False, 'message': '请提供旧密码和新密码'}, status=400)
    
    if not request.user.check_password(old_password):
        return JsonResponse({'success': False, 'message': '旧密码不正确'}, status=400)
    
    if len(new_password) < 6:
        return JsonResponse({'success': False, 'message': '新密码至少需要6个字符'}, status=400)
    
    request.user.set_password(new_password)
    request.user.save()
    
    return JsonResponse({'success': True, 'message': '密码修改成功'})
