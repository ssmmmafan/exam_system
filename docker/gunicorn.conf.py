bind = '0.0.0.0:8000'
workers = 4

# 静态文件配置
pythonpath = '/app'

# 环境变量
raw_env = [
    'DEBUG=True',
    'SECRET_KEY=2b8c4e6f8a0b2c4d6e8f0a2b4c6d8e0f',
    'DATABASE_URL=mysql://root:zxcvbnm134@db:3306/exam_system_db'
]
