# ProductsShow 开发文档

## 项目概述

ProductsShow是一个基于Django和Django REST Framework的产品展示和管理系统，旨在提供WooCommerce兼容的产品管理功能，包括产品创建、编辑、导入导出等功能。

## 技术栈

- **后端框架**: Django 5.2 + Django REST Framework
- **数据库**: MySQL
- **认证**: 基于JWT的认证系统
- **API文档**: Django REST Framework内置OpenAPI文档
- **前端**: （待定义）

## 项目结构

```
productsShow/
├── common/               # 通用组件（响应处理、异常处理、中间件等）
├── docs/                 # 业务文档相关应用
├── exports/              # 数据导出功能
├── imports/              # 数据导入功能
├── media/                # 媒体文件（用户上传的图片等）
├── products/             # 产品管理应用
├── product_show/         # 项目核心配置
├── static/               # 静态文件
├── staticfiles/          # 收集的静态文件（生产环境）
├── templates/            # HTML模板
└── users/                # 用户认证和管理
```

## 核心模型

### 产品模型

产品模型设计基于WooCommerce产品结构，支持简单产品、变体产品、组合产品和外部产品。

#### Product (主产品)

```python
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    sku = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='simple')
    # 其他产品基本信息字段
    menu_order = models.IntegerField(default=0, help_text="WooCommerce产品排序字段，值越小排序越靠前")
    # ...
```

#### ProductVariation (产品变体)

```python
class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    sku = models.CharField(max_length=100, unique=True)
    # 变体特有的属性和价格信息
    # ...
```

#### 产品属性系统

```python
class Attribute(models.Model):
    name = models.CharField(max_length=100)
    # ...

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    name = models.CharField(max_length=100)
    # ...

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    # ...

class VariationAttribute(models.Model):
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    # ...
```

### 用户模型

使用自定义User模型和JWT认证系统：

```python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    # ...

class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255)
    # ...
```

## API设计

项目使用Django REST Framework构建API，支持以下主要功能：

### 用户认证API

- `/api/v1/users/register/` - 用户注册
- `/api/v1/users/login/` - 用户登录
- `/api/v1/users/logout/` - 用户登出
- `/api/v1/users/token/refresh/` - 刷新令牌
- `/api/v1/users/profile/` - 用户信息管理

### 产品管理API

- `/api/v1/products/` - 产品列表和创建
- `/api/v1/products/<id>/` - 单个产品详情、更新和删除
- `/api/v1/products/<id>/variations/` - 产品变体管理
- `/api/v1/categories/` - 产品分类管理
- `/api/v1/attributes/` - 产品属性管理

### 导入导出API

- `/api/v1/imports/products/` - 产品导入
- `/api/v1/exports/products/` - 产品导出

## 导入导出功能

项目支持WooCommerce兼容的CSV格式产品导入导出：

### 导出格式

产品导出CSV包含以下关键字段：

- `ID` - 产品ID
- `Type` - 产品类型（simple, variable等）
- `SKU` - 产品SKU
- `Name` - 产品名称
- `Menu order` - 产品排序顺序（只用于主产品）
- 其他产品相关字段...

### 导入处理

导入处理流程：

1. 解析上传的CSV文件
2. 验证数据合法性
3. 创建或更新产品记录
4. 处理产品关联数据（分类、属性、变体等）
5. 返回导入结果报告

## 开发规范

### 代码风格

- 遵循PEP 8规范
- 类名使用CamelCase
- 函数和变量名使用snake_case
- 添加适当的文档字符串

### API响应格式

统一的API响应格式：

```json
{
  "code": 2000,  // 业务状态码
  "message": "操作成功",  // 操作结果描述
  "data": {  // 数据载荷
    // 具体数据...
  }
}
```

### 异常处理

使用自定义异常和统一的异常处理中间件：

```python
# common/exceptions.py
class BusinessException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.message)

# 异常处理中间件
def custom_exception_handler(exc, context):
    # 处理异常并返回统一格式的响应...
```

## 配置管理

核心配置位于`product_show/settings.py`：

- 数据库配置
- JWT认证配置
- REST Framework配置
- 静态文件和媒体文件配置

## API文档

项目集成了Django REST Framework的OpenAPI文档：

- Swagger UI: `/swagger-ui/`
- ReDoc: `/redoc/`
- 原始OpenAPI模式: `/openapi/`

## 部署指南

### 开发环境部署

1. 克隆代码库
2. 创建虚拟环境
3. 安装依赖: `pip install -r requirements.txt`
4. 配置数据库
5. 运行迁移: `python manage.py migrate`
6. 启动开发服务器: `python manage.py runserver`

### 生产环境部署

1. 设置环境变量
2. 收集静态文件: `python manage.py collectstatic`
3. 配置生产级Web服务器（Nginx, uWSGI等）
4. 设置适当的安全措施
5. 启用HTTPS

## 测试策略

- 单元测试: `python manage.py test`
- API测试: 使用`APITestCase`
- 集成测试: 测试关键业务流程
