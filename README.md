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
- **聊天中心**：私聊、考试讨论区，WebSocket 实时推送消息

---

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端框架 | Django 6.0.3 + Python 3.12 |
| 实时通信 | Django Channels 4.x + WebSocket |
| 数据库 | MySQL 8.0 |
| 前端框架 | Vue 3.4.21 + TypeScript 6.0 |
| 构建工具 | Vite 5.x |
| 路由 | Vue Router 5.x |
| HTTP 请求 | Axios 1.6.x |
| 容器化 | Docker + Docker Compose |
| ASGI 服务器 | Daphne 4.x（开发/Docker，支持 WebSocket） |
| WSGI 服务器 | Gunicorn 21.x（纯 HTTP 生产场景） |
| 数据处理 | Pandas + OpenPyXL |
| 消息广播（可选） | Redis（多进程/多容器部署聊天室时推荐） |

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

### 📦 方式一：Docker Compose 部署（推荐，一键启动）

> 无需手动安装 Python/Node.js/MySQL，一条命令启动全部服务。

#### 一、首次部署

```bash
# 1. 进入项目目录
cd exam_system

# 2. 一键启动所有服务（后台运行）
docker-compose up -d

# 3. 查看运行状态
docker-compose ps

# 4. 初始化数据库
docker-compose exec web python manage.py migrate

# 5. 创建超级管理员
docker-compose exec web python manage.py createsuperuser

# 6. 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

> **提示**：后续如果修改了模型（新增字段等），只需重新运行 `docker-compose exec web python manage.py migrate` 即可，无需重建容器。

#### 二、日常启动与停止

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 启动所有服务（前台运行，按 Ctrl+C 停止）
docker-compose up

# 启动单个服务（如 web 后端）
docker-compose up -d web

# 停止所有服务（保留数据库数据）
docker-compose down

# 停止所有服务并删除数据卷（清空数据库和上传文件）
docker-compose down -v

# 停止单个服务
docker-compose stop web
```

#### 三、重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart web
docker-compose restart frontend
docker-compose restart nginx
```

#### 四、查看状态与日志

```bash
# 查看各服务运行状态
docker-compose ps

# 实时查看后端日志（按 Ctrl+C 退出）
docker-compose logs -f web

# 查看前端日志
docker-compose logs -f frontend

# 查看最近 50 行日志
docker-compose logs --tail=50 web
```

#### 五、重新构建

```bash
# 重新构建后端镜像（修改依赖或 Dockerfile 后需要）
docker-compose build --no-cache web

# 重新构建并启动
docker-compose up -d --build web
```

#### 六、容器内部操作

```bash
# 进入后端容器（Shell 环境）
docker-compose exec web bash

# 进入数据库容器
docker-compose exec db bash

# 在容器内执行 Django 命令
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# 检查数据库连接
docker-compose exec db mysql -uroot -pzxcvbnm134 exam_system_db
```

#### Docker 访问地址

| 服务 | 地址 |
|------|------|
| 📄 前端页面 | http://localhost |
| ⚙️ Django Admin | http://localhost/admin/ |
| 🔗 API 接口 | http://localhost/api/ |
| 💬 WebSocket 聊天 | `ws://localhost/ws/chat/{conversation_id}/` |

> **说明**：Docker 后端已使用 **Daphne（ASGI）** 启动，Nginx 已配置 `/ws/` 反向代理，聊天室 WebSocket 可直接使用。  
> 多容器/多进程部署聊天室时，建议为 `web` 服务配置环境变量 `REDIS_URL=redis://redis:6379/0` 并添加 Redis 服务。

---

### 💻 方式二：开发模式（前后端分离）

> 需要本地安装 Python 3.12+、Node.js 18+、MySQL 8.0+。

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

# 启动后端服务（端口 8000，推荐 Daphne，支持 WebSocket 聊天室）
daphne -b 127.0.0.1 -p 8000 exam_system.asgi:application
```

> **聊天室 WebSocket 说明**  
> - 聊天消息通过 WebSocket 实时推送，路径：`ws://localhost:8000/ws/chat/{conversation_id}/`  
> - 开发模式下前端走 Vite 代理，实际连接地址为：`ws://localhost:5173/ws/chat/{conversation_id}/`  
> - 若未安装 Daphne，也可使用 `python manage.py runserver 0.0.0.0:8000`（已安装 `channels` 时同样支持 WebSocket）  
> - 仅使用 Gunicorn + WSGI **无法**使用聊天室 WebSocket

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
| 📄 前端页面 | http://localhost:5173 |
| 💬 聊天中心 | http://localhost:5173/chat |
| ⚙️ Django Admin | http://localhost:8000/admin/ |
| 🔗 API 接口 | http://localhost:8000/api/ |
| 🔌 WebSocket | `ws://localhost:5173/ws/chat/{conversation_id}/` |

#### 5. 本地开发启动命令速查

需要 **两个终端** 同时运行：

**终端 1 — 后端（二选一）**

```bash
cd exam_system
pip install -r requirements.txt

# 推荐：Daphne（ASGI，完整支持 WebSocket）
daphne -b 127.0.0.1 -p 8000 exam_system.asgi:application

# 或：Django 开发服务器（已安装 channels 时同样支持 WebSocket）
python manage.py runserver 0.0.0.0:8000
```

**终端 2 — 前端**

```bash
cd exam_system
npm install
npm run dev
```

启动后访问 http://localhost:5173 ，登录后可通过首页「聊天中心」或考试详情页「考试讨论区」进入聊天。

---

### 🚀 方式三：生产模式构建

```bash
# 1. 构建前端
npm run build
# 产物输出到 dist/ 目录

# 2. 配置 Django settings.py
# DEBUG = False
# SECRET_KEY = 'your-secret-key'
# 若启用聊天室 WebSocket，建议配置 REDIS_URL

# 3. 收集静态文件
python manage.py collectstatic --noinput

# 4. 启动后端（需 WebSocket 时使用 Daphne）
daphne -b 0.0.0.0 -p 8000 exam_system.asgi:application

# 若仅需 HTTP、不使用聊天 WebSocket，可使用 Gunicorn
# gunicorn exam_system.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 项目结构

```
exam_system/
├── exam_system/              # Django 项目配置
│   ├── settings.py           # 配置文件（数据库、静态文件等）
│   ├── urls.py               # 根路由
│   ├── asgi.py               # ASGI 入口（HTTP + WebSocket）
│   ├── wsgi.py               # WSGI 入口
│   └── __init__.py
├── chat/                     # 聊天应用（WebSocket 实时消息）
│   ├── models.py             # ChatConversation, ChatMessage
│   ├── consumers.py          # WebSocket Consumer
│   ├── api_views.py          # 聊天 REST API
│   └── routing.py            # WebSocket 路由
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
│       ├── Chat.vue            # 聊天中心
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

开发模式下，Vite 自动将请求代理到 Django 后端，配置在 `vite.config.ts` 中：

| 路径 | 代理目标 | 用途 |
|------|----------|------|
| `/api` | `http://localhost:8000` | REST API |
| `/ws` | `ws://localhost:8000` | 聊天 WebSocket |

生产模式下，需通过 Nginx 将 `/api/` 和 `/ws/` 转发到 Django（Daphne）后端。

### 聊天室 Channel Layer

默认使用内存 Channel Layer（单进程开发足够）。多 worker / Docker 多实例部署时，请配置 Redis：

```bash
# 环境变量示例
REDIS_URL=redis://127.0.0.1:6379/0
```

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

### 聊天

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/conversations/` | GET | 会话列表 |
| `/api/chat/conversations/create/` | POST | 创建私聊/考试聊天室 |
| `/api/chat/conversations/<id>/` | GET | 会话消息（打开时标记已读） |
| `/api/chat/conversations/<id>/send/` | POST | 发送消息（并 WebSocket 广播） |
| `/api/chat/exams/<exam_id>/conversation/` | POST | 进入/创建考试讨论区 |
| `/ws/chat/<conversation_id>/` | WebSocket | 实时接收新消息 |

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
- 检查 `vite.config.ts` 中的 proxy 配置（`/api` 与 `/ws`）
- 重启 Vite 开发服务器

### 3. 聊天室 WebSocket 连接失败

页面显示「连接中...」或消息不能实时更新时：
- 确认后端使用 **Daphne** 或 `runserver` 启动，而不是 Gunicorn WSGI
- 确认启动命令：`daphne -b 127.0.0.1 -p 8000 exam_system.asgi:application`
- 开发模式需同时启动前端 `npm run dev`（Vite 代理 `/ws`）
- Docker 部署需确认 Nginx 已配置 `/ws/` 反向代理
- 多进程部署需配置 `REDIS_URL`，否则广播可能失效

### 4. 头像上传失败

- 确认 `media/` 目录存在且可写
- 检查 Django 是否配置了 `MEDIA_URL` 和 `MEDIA_ROOT`
- 重启 Django 服务器

### 5. 批量导入题目失败

- 确认 Excel 文件格式正确
- 检查表头是否匹配系统要求的格式
- 确认无重复的题目编号

### 6. Docker 部署问题

```bash
# 查看详细日志
docker-compose logs -f

# 进入容器调试
docker-compose exec web bash

# 检查数据库连接
docker-compose exec db mysql -uroot -pzxcvbnm134 exam_system_db
```

---

## 生成公网访问地址（Serveo）

使用 Serveo SSH 隧道将本地服务暴露到公网，方便演示或移动端测试：

```bash
# 将 Django 后端（8000 端口）暴露到公网
ssh -R 80:localhost:8000 serveo.net

# 或使用自定义子域名
ssh -R myexam:80:localhost:8000 serveo.net

# 同时暴露 Django 后端和前端
ssh -R 80:localhost:8000 -R 80:localhost:5173 serveo.net
```

执行后会生成一个 `https://xxx.serveo.net` 格式的公网地址，通过该地址即可从外部访问系统。

---

## 许可证

本项目仅供学习和教学使用。