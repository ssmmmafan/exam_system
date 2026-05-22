# 在线考试系统

基于 **Django 6.0 + Vue 3 + MySQL** 开发的在线考试系统，支持教师创建考试、管理题库，学生参加考试、查看成绩。

---

## 功能特点

### 教师功能
- **题库管理**：创建、编辑、批量导入题目（支持 Excel/CSV）
- **考试管理**：创建考试、随机组卷、自定义分数设置
- **防作弊**：随机题目顺序、随机选项顺序
- **试卷批改**：自动批改客观题（单选/多选/判断/填空），手动批改主观题（简答/论述）
- **学生管理**：查看考试状态、成绩统计、试卷详情

### 学生功能
- **注册登录**：学生注册并关联教师
- **参加考试**：支持多种题型，实时倒计时，题目导航
- **成绩查看**：历史考试成绩和详细答题情况、错题本

### 系统特点
- **支持题型**：单选题、多选题、判断题、填空题、简答题、论述题
- **批量导入**：支持 Excel/CSV 文件导入题目
- **随机组卷**：按题型和数量自动生成试卷
- **个人中心**：支持修改资料、更换头像

---

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端框架 | Django 6.0.3 + Python 3.12 |
| 数据库 | MySQL 8.0 |
| 前端框架 | Vue 3.4.21 + TypeScript 6.0 |
| 构建工具 | Vite 5.x |
| 路由 | Vue Router 5.x |
| HTTP 请求 | Axios 1.6.x |
| 容器化 | Docker + Docker Compose |
| WSGI 服务器 | Gunicorn 21.x |
| 数据处理 | Pandas + OpenPyXL |

---

## 前置要求

### 本地开发
- Python 3.12+
- Node.js 18+
- MySQL 8.0+
- npm 或 yarn

### Docker 部署
- Docker 24+
- Docker Compose 2.20+

---

## 快速启动

### 方式一：开发模式（前后端分离，推荐）

#### 1. 配置数据库

确保 MySQL 服务已启动，创建数据库：

```sql
CREATE DATABASE exam_system_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2. 配置后端

```bash
# 进入项目目录
cd exam_system

# 安装 Python 依赖
pip install -r requirements.txt

# 修改数据库配置（如果需要）
# 编辑 exam_system/settings.py 中的 DATABASES 配置

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动后端服务（端口 8000）
python manage.py runserver 0.0.0.0:8000
```

#### 3. 配置前端（新终端）

```bash
# 进入项目目录
cd exam_system

# 安装 Node.js 依赖
npm install

# 启动前端开发服务器（端口 5173）
npm run dev
```

#### 4. 访问系统

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| Django API | http://localhost:8000 |
| Django Admin | http://localhost:8000/admin/ |

---

### 方式二：Docker Compose 部署（一键启动）

```bash
# 1. 进入项目目录
cd exam_system

# 2. 启动所有服务
docker-compose up -d

# 3. 查看运行状态
docker-compose ps

# 4. 初始化数据库（首次运行）
docker-compose exec web python manage.py migrate

# 5. 创建超级管理员
docker-compose exec web python manage.py createsuperuser

# 6. 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

访问地址：
- 前端页面：http://localhost:5173
- Django Admin：http://localhost （通过 Nginx 反向代理）
- API 接口：http://localhost/api/

Docker 常用命令：
```bash
# 停止服务
docker-compose down

# 停止并删除数据卷（清空数据库）
docker-compose down -v

# 查看日志
docker-compose logs -f web
docker-compose logs -f frontend

# 重启某个服务
docker-compose restart web

# 重新构建
docker-compose build --no-cache web
```

---

### 方式三：生产模式构建

```bash
# 1. 构建前端
npm run build
# 产物输出到 dist/ 目录

# 2. 配置 Django settings.py
# DEBUG = False
# SECRET_KEY = 'your-secret-key'

# 3. 收集静态文件
python manage.py collectstatic --noinput

# 4. 使用 Gunicorn 启动
gunicorn exam_system.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 项目结构

```
exam_system/
├── exam_system/              # Django 项目配置
│   ├── settings.py           # 配置文件（数据库、静态文件等）
│   ├── urls.py               # 根路由
│   ├── wsgi.py               # WSGI 入口
│   └── __init__.py
├── exams/                    # 考试应用（模型：考试、题目）
│   ├── models.py             # Exam, ExamQuestion
│   └── ...
├── students/                 # 学生应用（模型：学生、答题记录）
│   ├── models.py             # StudentProfile, StudentExamRecord
│   ├── api_views.py          # 学生端 API
│   └── api_urls.py           # 学生端路由
├── teachers/                 # 教师应用
│   ├── api_views.py          # 教师端 API
│   └── api_urls.py           # 教师端路由
├── users/                    # 用户认证应用
│   └── ...
├── api/                      # API 路由聚合
│   └── urls.py
├── docker/                   # Docker 配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── src/                      # Vue 3 前端源码
│   ├── main.ts               # 入口文件
│   ├── App.vue               # 根组件
│   ├── router/
│   │   └── index.ts          # 路由配置
│   ├── utils/
│   │   └── api.ts            # Axios 封装
│   ├── components/           # 公共组件
│   │   ├── StudentSidebar.vue
│   │   └── TeacherSidebar.vue
│   └── views/
│       ├── student/          # 学生页面
│       │   ├── Dashboard.vue
│       │   ├── Exams.vue
│       │   ├── ExamTaking.vue
│       │   ├── ExamDetail.vue
│       │   ├── ResultDetail.vue
│       │   ├── WrongQuestions.vue
│       │   └── Profile.vue
│       └── teacher/          # 教师页面
│           ├── Dashboard.vue
│           ├── QuestionBank.vue
│           ├── ExamManagement.vue
│           ├── ExamDetail.vue
│           ├── CreateExam.vue
│           ├── GradeExam.vue
│           ├── TeacherExamResult.vue
│           └── StudentManagement.vue
├── manage.py                 # Django 管理脚本
├── requirements.txt          # Python 依赖
├── package.json              # Node.js 依赖
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
├── docker-compose.yml        # Docker Compose 配置
└── README.md
```

---

## 配置说明

### 数据库配置

默认使用 MySQL，配置位于 `exam_system/settings.py`：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'exam_system_db',
        'USER': 'root',
        'PASSWORD': 'zxcvbnm134',
        'HOST': 'localhost',
        'PORT': 3306,
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

### 前端代理配置

开发模式下，Vite 自动将 `/api` 请求代理到 `http://localhost:8000`，配置在 `vite.config.ts` 中。

生产模式下，需通过 Nginx 或其他方式将 API 请求转发到 Django 后端。

### 媒体文件

头像等用户上传文件存储在 `media/` 目录下，Django 开发环境自动提供媒体文件路由：

```
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 用户指南

### 教师操作流程

1. **登录**：使用管理员或教师账号登录系统
2. **题库管理**：创建题目（单选、多选、判断、填空、简答、论述），或通过 Excel 批量导入
3. **创建考试**：选择题目、设置分数、配置随机策略
4. **发布考试**：考试对学生可见
5. **批改试卷**：客观题自动批改，主观题手动评分
6. **查看成绩**：统计学生考试成绩

### 学生操作流程

1. **注册登录**：注册账号并关联教师
2. **参加考试**：在"我的考试"中选择待参加的考试
3. **答题**：按顺序作答，可标记题目，倒计时结束时自动提交
4. **查看成绩**：在"考试成绩"中查看已批改的试卷详情
5. **错题本**：复习做错的题目

### 账户类型

| 类型 | 创建方式 | 权限 |
|------|----------|------|
| 超级管理员 | `python manage.py createsuperuser` | 全部权限 |
| 教师用户 | 在 Django Admin 中创建 | 教师端功能 |
| 学生用户 | 前端注册页面 | 学生端功能 |

---

## API 接口

### 教师端

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/teacher/questions/` | GET | 获取题目列表 |
| `/api/teacher/questions/` | POST | 创建题目 |
| `/api/teacher/questions/import/` | POST | 批量导入题目 |
| `/api/teacher/questions/<id>/` | PUT/DELETE | 编辑/删除题目 |
| `/api/teacher/exams/` | GET | 获取考试列表 |
| `/api/teacher/exams/` | POST | 创建考试 |
| `/api/teacher/exam/<id>/` | GET/PUT/DELETE | 考试详情/编辑/删除 |
| `/api/teacher/exam/<id>/publish/` | POST | 发布考试 |
| `/api/teacher/exam/<id>/unpublish/` | POST | 取消发布 |
| `/api/teacher/grade/<record_id>/` | GET | 获取批改详情 |
| `/api/teacher/grade/<record_id>/submit/` | POST | 提交批改 |
| `/api/teacher/result/<record_id>/` | GET | 查看成绩详情 |
| `/api/teacher/students/` | GET | 学生列表 |

### 学生端

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/student/register/` | POST | 学生注册 |
| `/api/student/login/` | POST | 学生登录 |
| `/api/student/profile/` | GET/PUT | 获取/更新个人资料 |
| `/api/student/profile/avatar/` | POST | 上传头像 |
| `/api/student/exams/` | GET | 获取考试列表 |
| `/api/student/exam/<id>/` | GET | 考试详情 |
| `/api/student/exam/<id>/take/` | GET | 获取考试题目 |
| `/api/student/exam/<id>/submit/` | POST | 提交答卷 |
| `/api/student/results/` | GET | 考试成绩列表 |
| `/api/student/result/<record_id>/` | GET | 成绩详情 |
| `/api/student/wrong-questions/` | GET | 错题本 |

---

## 常见问题

### 1. MySQL 连接失败

```
错误: django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")
```

**解决**：
- 确认 MySQL 服务已启动
- 检查 `settings.py` 中的数据库配置
- Docker 部署时需检查 `docker-compose.yml` 中的数据库配置

### 2. 前端代理不生效

前端页面无法调用 API 时：
- 确认 Django 后端已启动（`http://localhost:8000`）
- 检查 `vite.config.ts` 中的 proxy 配置
- 重启 Vite 开发服务器

### 3. 头像上传失败

- 确认 `media/` 目录存在且可写
- 检查 Django 是否配置了 `MEDIA_URL` 和 `MEDIA_ROOT`
- 重启 Django 服务器

### 4. 批量导入题目失败

- 确认 Excel 文件格式正确
- 检查表头是否匹配系统要求的格式
- 确认无重复的题目编号

### 5. Docker 部署问题

```bash
# 查看详细日志
docker-compose logs -f

# 进入容器调试
docker-compose exec web bash

# 检查数据库连接
docker-compose exec db mysql -uroot -pzxcvbnm134 exam_system_db
```

---

## 许可证

本项目仅供学习和教学使用。