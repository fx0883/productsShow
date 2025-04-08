# 商品管理系统文档查看器部署指南

本文档提供了将商品管理系统文档查看器部署到cPanel托管服务的详细步骤。

## 目录

1. [准备工作](#准备工作)
2. [将项目文件上传到cPanel](#将项目文件上传到cpanel)
3. [创建Python应用](#创建python应用)
4. [配置虚拟环境](#配置虚拟环境)
5. [修改Django项目设置](#修改django项目设置)
6. [配置静态文件](#配置静态文件)
7. [配置passenger_wsgi.py](#配置passenger_wsgi文件)
8. [设置环境变量](#设置环境变量)
9. [重启应用](#重启应用)
10. [故障排除](#故障排除)

## 准备工作

在开始部署之前，请确保您有以下内容：

- cPanel主机账户及登录信息
- 有效的域名或子域名指向您的cPanel主机
- SSH访问权限（可选，但推荐）
- 项目所需的依赖已列在`requirements.txt`文件中

## 将项目文件上传到cPanel

1. 登录到cPanel控制面板
2. 使用File Manager或FTP工具将项目文件上传到服务器
   - 推荐路径：`public_html/doclist`（如果希望使用子目录）或 `public_html`（如果希望在网站根目录访问）

或者，如果您有SSH访问权限，可以使用Git克隆项目：

```bash
cd ~/public_html
git clone https://github.com/您的用户名/productsShow.git doclist
```

## 创建Python应用

1. 在cPanel控制面板中，找到并点击"Setup Python App"
2. 点击"Create Application"按钮
3. 填写以下信息：
   - Python版本：选择3.9或更高版本
   - 应用路径：输入您上传项目的路径（例如：/home/username/public_html/doclist）
   - 应用URL：选择您希望访问应用的URL（例如：https://yourdomain.com/doclist）
   - 应用启动文件：选择`passenger_wsgi.py`（稍后会创建此文件）
4. 点击"Create"按钮

## 配置虚拟环境

通过SSH连接到服务器，然后执行以下命令：

```bash
cd ~/public_html/doclist
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

如果没有SSH访问权限，请使用cPanel的Terminal功能执行上述命令。

## 修改Django项目设置

编辑`product_show/settings.py`文件，添加以下修改：

```python
# 将您的域名添加到ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# 设置DEBUG为False
DEBUG = False

# 配置静态文件
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 添加whitenoise中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 添加这一行
    # ... 其他中间件
]

# 配置静态文件存储
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## 配置静态文件

收集所有静态文件到STATIC_ROOT目录：

```bash
cd ~/public_html/doclist
source venv/bin/activate
python manage.py collectstatic
```

## 配置passenger_wsgi文件

在项目根目录创建`passenger_wsgi.py`文件：

```python
import os
import sys

# 将项目路径添加到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_show.settings')

# 导入Django的WSGI应用
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 设置环境变量

创建`.env`文件存储敏感信息和环境变量：

```bash
cd ~/public_html/doclist
echo "SECRET_KEY=your_secret_key_here" > .env
echo "DJANGO_SETTINGS_MODULE=product_show.settings" >> .env
```

确保`.env`文件不会被公开访问：

```bash
chmod 600 .env
```

## 重启应用

1. 在cPanel控制面板中，找到"Setup Python App"
2. 找到您的应用，点击"Restart"按钮

或者通过SSH执行：

```bash
touch ~/public_html/doclist/tmp/restart.txt
```

## 故障排除

### 常见问题

1. **500内部服务器错误**
   - 检查cPanel错误日志
   - 确认`passenger_wsgi.py`文件格式正确
   - 验证所有依赖已正确安装

2. **静态文件无法加载**
   - 确认`collectstatic`命令已成功运行
   - 检查STATIC_URL和STATIC_ROOT配置
   - 确认`whitenoise`中间件已添加

3. **无法连接到数据库**
   - 确认数据库设置正确
   - 检查数据库用户权限

### 查看日志

cPanel通常在以下位置存储错误日志：

```
~/logs/error_log
```

查看应用程序日志：

```bash
cd ~/public_html/doclist
cat application.log
```

## 结论

按照上述步骤，您应该能够成功将商品管理系统文档查看器部署到cPanel托管服务上。如果遇到任何问题，请参考故障排除部分或联系您的托管服务提供商获取支持。

部署完成后，您可以通过配置的URL（如https://yourdomain.com/doclist/）访问您的文档查看器。
