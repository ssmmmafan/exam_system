from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.login_api, name='login_api'),
    path('logout/', api_views.logout_api, name='logout_api'),
    path('change-password/', api_views.change_password_api, name='change_password_api'),
]
