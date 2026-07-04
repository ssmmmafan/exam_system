"""
WSGI config for exam_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import os.path

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')

# 确保静态文件目录存在
static_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles')
if not os.path.exists(static_root):
    os.makedirs(static_root, exist_ok=True)

# 先创建应用
application = get_wsgi_application()

# 配置Whitenoise
application = WhiteNoise(
    application,
    root=static_root,
    prefix='static/',
    index_file='index.html'
)
