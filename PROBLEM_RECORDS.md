# 考试系统问题记录与解决方案

本文档记录了考试系统开发和部署过程中遇到的各种问题、原因分析、解决方案以及技术原理。

## 问题1：数据库迁移错误

### 问题描述

```
OperationalError at /admin/exams/exam/ (1054, "Unknown column 'exam.random_questions' in 'field list'")
```

### 发生原因

- 在模型中添加了新字段 `random_questions`
- 但没有运行数据库迁移命令，导致数据库表结构与模型定义不匹配

### 解决办法

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate
```

### 原理解释

Django的ORM系统使用迁移文件来跟踪模型的变化。当模型发生变化时，需要通过 `makemigrations` 生成迁移文件，然后通过 `migrate` 命令将这些变化应用到数据库中。

### 反思

在修改模型后，必须及时运行迁移命令，否则会导致数据库结构与模型定义不一致，引发运行时错误。

## 问题2：批量导入按钮不可见

### 问题描述

教师后台看不到批量导入试题的按钮

### 发生原因

- 批量导入功能已实现，但在教师后台侧边栏模板中没有添加相应的链接

### 解决办法

在 `teachers/templates/teachers/base_teacher.html` 文件中添加批量导入链接：

```html
<li class="nav-item">
  <a class="nav-link" href="{% url 'teachers:import_questions' %}">批量导入题目</a>
</li>
```

### 原理解释

Django的模板系统使用模板继承，侧边栏导航是在基础模板中定义的。需要在基础模板中添加新功能的导航链接，才能在所有教师页面中显示。

### 反思

添加新功能时，不仅要实现后端逻辑，还要确保前端导航和UI元素也相应更新，保证功能的可访问性。

## 问题3：Docker部署中的静态文件加载问题

### 问题描述

Docker部署的系统界面没有样式，CSS、JS等静态文件无法加载，显示为纯文本界面

### 发生原因

1. **静态文件目录不存在**：容器中没有创建 `staticfiles` 目录
2. **Whitenoise配置不当**：WSGI应用中Whitenoise中间件配置不正确
3. **静态文件收集问题**：虽然运行了 `collectstatic` 命令，但静态文件可能没有正确复制

### 解决办法

1. **创建静态文件目录**：在Dockerfile中添加创建目录的步骤
   ```dockerfile
   RUN mkdir -p staticfiles
   RUN python manage.py collectstatic --noinput
   ```
2. **优化Whitenoise配置**：修改 `wsgi.py` 文件
   ```python
   # 配置Whitenoise
   application = WhiteNoise(
       application,
       root=static_root,
       prefix='static/',
       index_file='index.html'
   )
   ```
3. **确保ALLOWED\_HOSTS配置**：在settings.py中设置
   ```python
   ALLOWED_HOSTS = ['*']
   ```

### 原理解释

- **静态文件收集**：Django的 `collectstatic` 命令会将所有应用的静态文件复制到 `STATIC_ROOT` 指定的目录
- **Whitenoise中间件**：在生产环境中，Gunicorn等WSGI服务器不会自动提供静态文件服务，需要使用Whitenoise等中间件来处理静态文件请求
- **路径配置**：Whitenoise需要正确配置静态文件的根目录和URL前缀，才能正确映射静态文件请求

### 反思

在容器化部署时，需要特别注意文件路径和目录结构，确保所有必要的目录都已创建，并且配置文件中的路径设置正确。

## 问题4：Docker中的数据库连接问题

### 问题描述

```
django.db.utils.OperationalError: (1045, "Access denied for user 'root'@'172.18.0.3' (using password: YES)")
```

### 发生原因

- Docker容器中的MySQL服务与web服务使用不同的网络环境
- 数据库密码配置不正确
- 容器启动顺序问题，web服务在数据库服务完全就绪前就尝试连接

### 解决办法

1. **统一数据库密码**：确保docker-compose.yml中的数据库密码与应用配置一致
2. **删除旧容器和卷**：使用 `docker-compose down -v` 彻底清理环境
3. **重新构建和启动**：确保数据库服务完全就绪后再启动web服务

### 原理解释

Docker Compose会为服务创建一个内部网络，服务之间通过服务名进行通信。web服务通过 `db` 服务名连接到MySQL数据库，需要确保数据库服务已完全启动并且用户和密码配置正确。

### 反思

在多容器部署时，需要注意服务的启动顺序和依赖关系，确保服务之间能够正确通信。

##
