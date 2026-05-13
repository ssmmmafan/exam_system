# 在线考试系统

## 项目简介

这是一个基于Django开发的在线考试系统，用于软件工程课程大作业。系统支持教师创建考试、管理题库，学生参加考试、查看成绩等功能。

## 功能特点

### 教师功能

- 题库管理：创建、编辑、批量导入题目
- 考试管理：全新的考试管理功能，整合进行中考试、待批改试卷、我的考试等
- 智能组卷：手动创建考试、随机组卷，系统自动计算总分
- 防作弊措施：随机题目顺序、随机选项顺序
- 试卷批改：自动批改客观题，手动批改主观题
- 学生管理：查看学生考试状态，包括未参加、进行中、待批改、已批改
- 成绩统计：查看考试统计信息和学生成绩

### 学生功能

- 用户注册和登录
- 参加考试：支持多种题型
- 查看成绩：查看历史考试成绩和详细答题情况
- 考试监控：实时倒计时和自动保存答案

### 系统特点

- 支持多种题型：单选题、多选题、判断题、简答题、填空题、论述题
- 批量导入题目：支持从Excel/CSV文件导入题目
- 随机组卷：根据题型和数量自动生成试卷
- 性能优化：使用缓存和批量查询提高系统响应速度
- 安全可靠：权限控制和数据验证

## 技术栈

- **后端**：Python 3.13 + Django 6.0.3
- **数据库**：MySQL
- **前端**：HTML + CSS + JavaScript + Bootstrap 5
- **其他**：pandas（用于批量导入）

## 安装部署

### 方法一：传统部署

#### 1. 环境准备

1. 安装Python 3.13或更高版本
2. 安装MySQL数据库
3. 安装依赖包

#### 2. 安装步骤

1. 克隆项目到本地
   ```bash
   git clone <项目地址>
   cd exam_system
   ```
2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
3. 配置数据库
   - 修改 `exam_system/settings.py` 中的数据库配置
   - 创建数据库 `exam_system_db`
4. 运行数据库迁移
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. 创建超级用户
   ```bash
   python manage.py createsuperuser
   ```
6. 启动开发服务器
   ```bash
   python manage.py runserver
   ```
7. 访问系统
   - 管理后台：<http://127.0.0.1:8000/admin/>
   - 系统首页：<http://127.0.0.1:8000/>

### 方法二：Docker部署

#### 1. 环境准备

1. 安装Docker
2. 安装Docker Compose

#### 2. 部署步骤

1. 克隆项目到本地
   ```bash
   git clone <项目地址>
   cd exam_system
   ```
2. 修改配置
   - 编辑 `docker-compose.yml` 文件，设置合适的 `SECRET_KEY`
3. 启动服务
   ```bash
   docker-compose up -d
   ```
4. 运行数据库迁移
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```
5. 创建超级用户
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
6. 访问系统
   - 管理后台：<http://localhost:8000/admin/>
   - 系统首页：<http://localhost:8000/>

#### 3. Docker部署优势

- 环境隔离：避免依赖冲突
- 一键部署：简化部署流程
- 可移植性：在任何支持Docker的环境中运行
- 易于扩展：方便添加其他服务

#### 4. 常用Docker命令（都需要在文件目录下cmd执行）

- 查看容器状态：`docker-compose ps`
- 查看日志：`docker-compose logs web`
- 停止服务：`docker-compose down`
- 重启服务：`docker-compose restart`

## 使用指南

### 教师操作

1. 登录系统后进入教师后台
2. 点击"题库管理"创建或导入题目
3. 点击"考试管理"创建考试或使用"随机组卷"生成试卷
4. 点击"待批改试卷"批改学生提交的试卷
5. 点击"进行中考试"查看考试状态和学生成绩

### 学生操作

1. 注册账号并登录系统
2. 在学生后台查看待参加的考试
3. 点击"进入考试"开始考试
4. 完成考试后提交试卷
5. 在"已完成的考试"中查看成绩

## 批量导入题目

1. 准备Excel或CSV文件，包含以下列：
   - type：题型（single/multiple/judge/essay/fill/discussion）
   - content：题目内容
   - options：选项（JSON格式，仅单选题和多选题）
   - answer：正确答案
   - score：分值
   - tags：标签（可选，多个标签用逗号分隔）
2. 点击侧边栏的"批量导入题目"
3. 上传文件并导入

## 系统结构

```
exam_system/
├── exam_system/          # 项目配置
├── exams/               # 考试应用
├── questions/           # 题目应用
├── students/            # 学生应用
├── teachers/            # 教师应用
├── users/               # 用户应用
├── manage.py            # 管理脚本
├── README.md            # 项目说明
├── requirements.txt     # 依赖包配置
├── Dockerfile           # Docker构建文件
└── docker-compose.yml   # Docker Compose配置
```

## 测试

运行测试确保系统功能正常：

```bash
python manage.py test
```

## 注意事项

1. 批量导入功能需要安装pandas和openpyxl库
2. 系统默认使用MySQL数据库，需要确保数据库服务正常运行
3. 生产环境部署时需要配置DEBUG=False和设置SECRET_KEY
4. 建议使用Nginx和Gunicorn进行生产环境部署
5. Docker部署时需要确保Docker服务正常运行
6. 系统已配置中国时区（Asia/Shanghai）和中文界面
7. 学生需要关联教师才能看到考试，教师可以管理所有学生的考试状态
8. 系统会自动计算考试总分，无需手动输入
9. 已结束但未参加的考试会自动移到历史考试中

## 许可证

本项目仅供学习和教学使用。

## 联系方式

如有问题，请联系：

- 邮箱：<admin@example.com>
- 电话：1234567890
- <br />

```
ssh -R myexam:80:localhost:8000 serveo.net
```

上面的命令可以让别人访问网站。可以注册获得稳定域名

```
 https://myexam.serveousercontent.com
```

