import requests
import os

class AdminAccessMiddleware:
    """
    中间件：只允许超级管理员访问admin后台
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated and not request.user.is_superuser:
                from django.contrib import messages
                from django.shortcuts import redirect
                
                messages.error(request, '您没有权限访问后台管理。')
                return redirect('/login/')
        
        response = self.get_response(request)
        return response


class ViteProxyMiddleware:
    """
    中间件：在开发环境中将前端资源请求转发到Vite开发服务器
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.vite_server = os.environ.get('VITE_SERVER', 'http://localhost:5175')
    
    def __call__(self, request):
        path = request.path
        
        if path.startswith('/src/') or path.startswith('/assets/') or \
           path.startswith('/@vite/') or path.startswith('/@id/') or \
           path.endswith('.ts') or path.endswith('.js') or path.endswith('.vue') or \
           path.endswith('.css') or path.endswith('.svg') or path.endswith('.png') or \
           path.endswith('.jpg') or path.endswith('.woff') or path.endswith('.woff2'):
            
            try:
                url = f"{self.vite_server}{path}"
                response = requests.get(url, stream=True)
                
                if response.status_code == 200:
                    from django.http import HttpResponse
                    return HttpResponse(
                        response.content,
                        content_type=response.headers.get('Content-Type', 'application/octet-stream')
                    )
            except Exception:
                pass
        
        return self.get_response(request)