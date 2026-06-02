from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import api_views

urlpatterns = [
    path('', csrf_exempt(api_views.login_api), name='login_api'),
    path('logout/', csrf_exempt(api_views.logout_api), name='logout_api'),
    path('change-password/', csrf_exempt(api_views.change_password_api), name='change_password_api'),
]
