# 项目文件结构说明

## 概述

本文档详细说明在线考试系统的文件结构和各模块的职责，帮助开发者快速理解项目架构。

## 项目目录结构

```
exam_system/                              # 项目根目录
├── exam_system/                          # Django项目配置目录
│   ├── __init__.py                       # Python包标记
│   ├── asgi.py                           # ASGI服务器配置（异步部署）
│   ├── settings.py                       # 项目配置文件（数据库、中间件、静态文件等）
│   ├── urls.py                           # 项目根URL配置
│   └── wsgi.py                           # WSGI服务器配置（同步部署）
├── exams/                                # 考试模块
│   ├── __init__.py
│   ├── admin.py                          # Django Admin配置
│   ├── apps.py                           # 应用配置
│   ├── migrations/                       # 数据库迁移文件
│   ├── models.py                         # 考试相关模型（Exam, ExamQuestion）
│   ├── tests.py                          # 单元测试
│   └── views.py                          # 考试相关视图（备用）
├── students/                             # 学生模块
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py                         # 学生相关模型（StudentProfile, StudentExamRecord, StudentAnswer）
│   ├── templates/                        # 学生端模板
│   │   └── students/                     # 学生模板目录
│   │       ├── base_student.html         # 学生端基础模板
│   │       ├── dashboard.html            # 学生首页（Django模板版）
│   │       ├── dashboard_vue.html        # 学生首页（Vue版）
│   │       ├── exam_taking.html          # 考试页面（Django模板版）
│   │       ├── exam_taking_vue.html      # 考试页面（Vue版）
│   │       ├── submit_confirm_vue.html   # 提交确认页面（Vue版）
│   │       └── result_detail.html        # 成绩详情页面
│   ├── templatetags/                     # 自定义模板标签
│   │   ├── __init__.py
│   │   └── vue_tags.py                   # Vue数据传递标签
│   ├── tests.py
│   ├── urls.py                           # 学生端URL配置
│   └── views.py                          # 学生端视图函数
├── teachers/                             # 教师模块
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py                         # 教师相关模型（TeacherProfile, Question, QuestionTag）
│   ├── templates/                        # 教师端模板
│   │   └── teachers/                     # 教师模板目录
│   │       ├── base_teacher.html         # 教师端基础模板
│   │       ├── dashboard.html            # 教师首页（Django模板版）
│   │       ├── dashboard_vue.html        # 教师首页（Vue版）
│   │       ├── question_management.html  # 试题管理页面
│   │       ├── exam_management.html      # 考试管理页面
│   │       └── grade_exam.html           # 试卷批改页面
│   ├── tests.py
│   ├── urls.py                           # 教师端URL配置
│   └── views.py                          # 教师端视图函数
├── users/                                # 用户认证模块
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py                         # 用户相关模型扩展
│   ├── templates/                        # 用户认证模板
│   │   └── users/
│   │       ├── login.html                # 登录页面
│   │       ├── register.html             # 注册页面
│   │       └── base.html                 # 用户认证基础模板
│   ├── tests.py
│   ├── urls.py                           # 用户认证URL配置
│   └── views.py                          # 用户认证视图函数
├── static/                               # 静态文件目录（开发环境）
│   ├── css/                              # CSS文件
│   ├── js/                               # JavaScript文件
│   │   └── vue-utils.js                  # Vue工具函数库
│   └── images/                           # 图片资源
├── staticfiles/                          # 静态文件目录（生产环境，collectstatic目标）
├── templates/                            # 全局模板
│   ├── base.html                         # 全站基础模板
│   ├── index.html                        # 系统首页
│   └── 404.html                          # 404错误页面
├── .gitignore                            # Git忽略配置
├── docker-compose.yml                    # Docker Compose配置
├── Dockerfile                            # Docker镜像构建配置
├── manage.py                             # Django管理脚本
├── requirements.txt                      # 依赖包列表
├── README.md                             # 项目说明文档
├── SYSTEM_INTRODUCTION.md                # 系统介绍文档
├── PROBLEM_RECORDS.md                    # 问题记录文档
└── ROADMAP.md                            # 项目路线图
```

## 目录职责说明

### 1. exam_system/（项目配置）
- **settings.py**：核心配置文件，包含数据库连接、静态文件路径、中间件、应用列表等
- **urls.py**：项目级URL路由，将请求分发到各个应用
- **wsgi.py/asgi.py**：服务器网关接口配置

### 2. exams/（考试模块）
- 管理考试的创建、发布、关联题目等核心逻辑
- **models.py**：定义Exam（考试）和ExamQuestion（考试题目关联）模型

### 3. students/（学生模块）
- 处理学生的考试参与、答题、成绩查询等功能
- **views.py**：学生端业务逻辑
- **templates/students/**：学生端UI模板，包含Vue版本和Django模板版本

### 4. teachers/（教师模块）
- 处理教师的题库管理、考试管理、试卷批改等功能
- **views.py**：教师端业务逻辑
- **templates/teachers/**：教师端UI模板

### 5. users/（用户认证模块）
- 处理用户注册、登录、权限验证等功能
- **views.py**：认证相关视图

### 6. static/（静态资源）
- 存放CSS、JavaScript、图片等静态文件
- **js/vue-utils.js**：封装Vue工具函数，简化Vue与Django的集成

### 7. templates/（全局模板）
- 存放全站共用的模板文件
- **base.html**：所有页面的基础模板，定义页面框架

## 文件命名规范

### 模板文件
- **base_*.html**：基础模板，供其他模板继承
- ***_vue.html**：Vue版本的页面模板
- ***.html**：纯Django模板版本

### Python文件
- **models.py**：数据库模型定义
- **views.py**：视图函数定义
- **urls.py**：URL路由配置
- **admin.py**：Django Admin配置

## 关键文件说明

### settings.py 关键配置
- **DATABASES**：数据库连接配置，支持Docker环境
- **INSTALLED_APPS**：已安装的应用列表
- **MIDDLEWARE**：中间件配置
- **STATIC_URL/STATIC_ROOT**：静态文件配置
- **TIME_ZONE**：时区设置（Asia/Shanghai）

### vue-utils.js 核心功能
- **VueUtils.createApp()**：简化Vue应用创建
- **VueUtils.ajax()**：封装HTTP请求，使用Promise
- **VueUtils.initFromDjango()**：从Django模板注入数据
- **VueUtils.showToast()**：消息提示组件

### views.py 命名规范
- **dashboard()**：首页视图
- **create_*()**：创建资源
- **edit_*()**：编辑资源
- **delete_*()**：删除资源
- ***_list()**：列表视图
- ***_detail()**：详情视图

## 开发流程建议

1. **新增功能**：
   - 在对应模块的 `views.py` 中添加视图函数
   - 在 `urls.py` 中添加路由配置
   - 在 `templates/` 中创建或修改模板
   - 如果涉及数据库变更，修改 `models.py` 并运行迁移

2. **修改功能**：
   - 优先查看相关视图函数和模板
   - 注意保持URL配置与模板链接的一致性

3. **调试技巧**：
   - 使用 `python manage.py runserver` 启动开发服务器
   - 使用Django Admin查看数据库数据
   - 使用浏览器开发者工具调试前端代码

---

**文档版本**：v1.0  
**更新日期**：2026年5月  
**适用项目**：在线考试系统
