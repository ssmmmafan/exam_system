class AdminAccessMiddleware:
    """
    中间件：阻止非超级管理员访问admin后台
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.user.is_superuser:
            from django.contrib import messages
            from django.shortcuts import redirect
            
            if request.user.is_authenticated and request.user.is_staff:
                messages.error(request, '您没有权限访问后台管理，请使用教师端功能。')
                return redirect('teachers:dashboard')
            else:
                return redirect('/login/')
        
        response = self.get_response(request)
        return response
