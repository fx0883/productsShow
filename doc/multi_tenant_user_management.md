# 多租户用户管理系统文档

## 目录

1. [概述](#1-概述)
   - [系统简介](#11-系统简介)
   - [主要功能概览](#12-主要功能概览)
   - [术语表](#13-术语表)

2. [架构设计](#2-架构设计)
   - [系统架构](#21-系统架构)
   - [数据模型](#22-数据模型)
   - [用户角色层级](#23-用户角色层级)
   - [安全机制](#24-安全机制)
   - [多租户设计](#25-多租户设计)

3. [API文档](#3-api文档)
   - [API概述](#31-api概述)
   - [认证与授权](#32-认证与授权)
   - [用户管理API](#33-用户管理api)
   - [超级用户管理API](#34-超级用户管理api)
   - [租户管理API](#35-租户管理api)
   - [租户用户API](#36-租户用户api)
   - [配额管理API](#37-配额管理api)

4. [部署与配置](#4-部署与配置)
   - [环境要求](#41-环境要求)
   - [安装步骤](#42-安装步骤)
   - [配置选项](#43-配置选项)
   - [数据库迁移](#44-数据库迁移)

5. [测试与质量保证](#5-测试与质量保证)
   - [测试策略](#51-测试策略)
   - [自动化测试](#52-自动化测试)
   - [测试用例说明](#53-测试用例说明)
   - [如何运行测试](#54-如何运行测试)

6. [使用示例与最佳实践](#6-使用示例与最佳实践)
   - [系统初始化](#61-系统初始化)
   - [超级用户创建与管理](#62-超级用户创建与管理)
   - [常见场景](#63-常见场景)
   - [集成示例](#64-集成示例)
   - [性能优化](#65-性能优化)

7. [故障排除与FAQ](#7-故障排除与faq)
   - [常见问题](#71-常见问题)
   - [错误码解释](#72-错误码解释)
   - [日志说明](#73-日志说明)

8. [扩展与定制](#8-扩展与定制)
   - [扩展点](#81-扩展点)
   - [自定义建议](#82-自定义建议)

## 1. 概述

### 1.1 系统简介

多租户用户管理系统是一个完整的解决方案，专为需要管理多个独立组织（租户）及其用户的应用程序设计。该系统提供了完整的用户身份验证、授权、租户隔离和资源配额管理功能，确保每个租户的数据安全隔离，同时提供统一的管理界面。

本系统基于Django和Django REST Framework构建，采用了JWT（JSON Web Token）进行身份验证，通过精心设计的权限模型确保不同角色的用户只能访问其权限范围内的资源。

### 1.2 主要功能概览

- **用户管理**：用户注册、登录、密码重置、个人资料管理
- **租户管理**：创建租户、管理租户状态、租户详情查看
- **多租户支持**：数据隔离、租户用户管理、租户间切换
- **角色管理**：超级管理员、租户管理员、普通用户
- **资源配额**：用户数量限制、存储空间限制、产品数量限制
- **权限控制**：基于角色的访问控制、租户内部权限
- **API接口**：RESTful API设计、完整的OpenAPI文档

### 1.3 术语表

| 术语 | 描述 |
|-----|------|
| **租户(Tenant)** | 系统中的独立组织单位，拥有自己的用户、数据和资源 |
| **超级管理员** | 可以管理所有租户和用户的系统级管理员 |
| **租户管理员** | 可以管理特定租户内用户的管理员 |
| **普通用户** | 租户内的标准用户，有限的权限和访问能力 |
| **配额(Quota)** | 限制租户可使用的资源数量，如用户数、存储空间等 |
| **软删除** | 标记记录为已删除而不是真正从数据库中移除 |
| **JWT** | JSON Web Token，用于用户身份验证的令牌机制 |
| **多租户** | 一个应用实例服务多个租户的架构模式 |

## 2. 架构设计

### 2.1 系统架构

多租户用户管理系统采用分层架构设计，主要包括以下几个层次：

1. **表示层**：RESTful API接口，使用Django REST Framework实现
2. **业务逻辑层**：视图集(ViewSets)和服务(Services)，处理核心业务逻辑
3. **数据访问层**：模型(Models)和管理器(Managers)，负责数据存取和查询优化
4. **基础设施层**：中间件、认证、权限和异常处理等基础组件

系统架构图：

```
┌────────────────────────────────────┐
│ 客户端 (Web/Mobile/API 消费者)      │
└────────────────┬───────────────────┘
                 │ HTTP/HTTPS
┌────────────────▼───────────────────┐
│  Django REST Framework API 层      │
│ ┌────────────────────────────────┐ │
│ │         认证中间件              │ │
│ │  (JWT Authentication)          │ │
│ └────────────────────────────────┘ │
│ ┌────────────────────────────────┐ │
│ │         租户中间件              │ │
│ │  (Tenant Context)              │ │
│ └────────────────────────────────┘ │
│ ┌────────────────────────────────┐ │
│ │        权限检查                 │ │
│ │  (Permission Classes)          │ │
│ └────────────────────────────────┘ │
└────────────────┬───────────────────┘
                 │
┌────────────────▼───────────────────┐
│           业务逻辑层                │
│ ┌────────────┐  ┌────────────────┐ │
│ │ 用户管理    │  │ 租户管理       │ │
│ └────────────┘  └────────────────┘ │
│ ┌────────────┐  ┌────────────────┐ │
│ │ 配额管理    │  │ 权限管理       │ │
│ └────────────┘  └────────────────┘ │
└────────────────┬───────────────────┘
                 │
┌────────────────▼───────────────────┐
│           数据访问层                │
│ ┌────────────┐  ┌────────────────┐ │
│ │ 模型定义    │  │ 查询管理器     │ │
│ └────────────┘  └────────────────┘ │
│ ┌────────────────────────────────┐ │
│ │ 租户过滤器 (TenantManager)     │ │
│ └────────────────────────────────┘ │
└────────────────┬───────────────────┘
                 │
┌────────────────▼───────────────────┐
│            数据库                   │
│ ┌────────────┐  ┌────────────────┐ │
│ │ 用户数据    │  │ 租户数据       │ │
│ └────────────┘  └────────────────┘ │
│ ┌────────────┐  ┌────────────────┐ │
│ │ 配额数据    │  │ 其他业务数据   │ │
│ └────────────┘  └────────────────┘ │
└────────────────────────────────────┘
```

### 2.2 数据模型

系统的核心数据模型设计如下：

#### Tenant（租户模型）
```python
class Tenant(models.Model):
    """租户模型，用于隔离不同租户的数据"""
    name = models.CharField("租户名称", max_length=100, unique=True)
    status = models.CharField("状态", max_length=20, 
                    choices=[('active', '活跃'), ('suspended', '暂停'), ('deleted', '已删除')], 
                    default='active')
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    is_deleted = models.BooleanField("是否删除", default=False)
```

#### User（用户模型）
```python
class User(AbstractUser):
    """用户模型，扩展自Django标准用户"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True)
    phone = models.CharField("手机号", max_length=20, null=True)
    email = models.EmailField("邮箱", unique=True)
    is_admin = models.BooleanField("是否管理员", default=False)
    is_member = models.BooleanField("是否成员", default=True)
    is_super_admin = models.BooleanField("是否超级管理员", default=False)
```

#### TenantQuota（租户配额模型）
```python
class TenantQuota(models.Model):
    """租户配额模型，用于限制租户的资源使用"""
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='quota')
    max_users = models.IntegerField("最大用户数", default=10)
    max_admins = models.IntegerField("最大管理员数", default=2)
    max_storage_mb = models.IntegerField("最大存储空间(MB)", default=1024)
    max_products = models.IntegerField("最大产品数", default=100)
    current_storage_used_mb = models.IntegerField("当前已用存储空间(MB)", default=0)
```

#### BaseModel（基础模型）
```python
class BaseModel(models.Model):
    """基础模型，所有需要租户隔离的模型都应该继承此模型"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    is_deleted = models.BooleanField("是否删除", default=False)
    
    objects = TenantManager()  # 自动过滤当前租户的查询管理器
    original_objects = models.Manager()  # 原始管理器，不过滤
    
    class Meta:
        abstract = True
```

### 2.3 用户角色层级

系统定义了清晰的用户角色层级：

1. **超级管理员 (Super Admin)**
   - 最高权限用户，可访问所有租户和功能
   - 可以创建、修改、删除租户
   - 可以分配或撤销租户管理员权限
   - 可以跨租户管理用户
   - 拥有`is_super_admin=True`标志

2. **租户管理员 (Tenant Admin)**
   - 特定租户内的管理用户
   - 可以管理本租户内的用户（创建、禁用等）
   - 可以查看和管理租户内的所有资源
   - 无法访问其他租户的数据
   - 拥有`is_admin=True`标志

3. **普通用户 (Regular User)**
   - 租户内的标准用户
   - 仅能访问被分配的资源和功能
   - 无法管理其他用户
   - 权限受到严格限制
   - 拥有`is_member=True`标志

权限继承关系：超级管理员 > 租户管理员 > 普通用户

### 2.4 安全机制

系统采用多层安全机制确保数据安全和访问控制：

1. **认证机制**
   - JWT (JSON Web Token) 认证
   - 令牌刷新和过期机制
   - 密码哈希和加盐存储

2. **授权机制**
   - 基于角色的访问控制 (RBAC)
   - 自定义权限类 (Permission Classes)
   - 操作级别的权限检查

3. **数据隔离**
   - 租户级别的数据过滤
   - 查询管理器自动添加租户过滤条件
   - 防止租户间数据泄露

4. **安全中间件**
   - CSRF保护
   - XSS防护
   - 租户上下文中间件

### 2.5 多租户设计

系统采用的多租户架构为"共享数据库，共享模式"（Shared Database, Shared Schema），具有以下特点：

1. **租户识别**
   - 通过HTTP请求中的JWT令牌识别当前用户
   - 从用户获取关联的租户信息
   - 中间件设置当前请求的租户上下文

2. **数据隔离**
   - 所有模型通过外键关联租户
   - 自定义查询管理器（TenantManager）自动添加租户过滤条件
   - 软删除机制保留历史数据同时确保隔离

3. **性能考量**
   - 租户字段添加数据库索引
   - 延迟加载减少不必要的查询
   - 针对大型租户的查询优化策略

4. **扩展性设计**
   - 支持未来迁移到分区表或独立数据库
   - 预留跨租户操作的接口和机制
   - 配额系统防止单一租户消耗过多资源

## 3. API文档

### 3.1 API概述

多租户用户管理系统提供了一组RESTful API，遵循以下设计原则：

1. **一致性**：所有API遵循统一的请求和响应格式
2. **版本控制**：API路径包含版本号（如`/api/v1/`）
3. **描述性**：URL和参数名称具有自描述性
4. **安全性**：所有API都需要适当的认证和授权
5. **文档化**：所有API都有完整的OpenAPI文档

#### 通用API响应格式

所有API返回统一的JSON格式：

```json
{
    "success": true,  // 请求是否成功
    "code": 2000,     // 业务状态码
    "message": "操作成功",  // 描述性消息
    "data": {},       // 实际返回数据
    "meta": {         // 元数据信息
        "timestamp": "2025-04-15T05:27:16.209460+00:00",
        "pagination": {
            "page": 1,
            "page_size": 10,
            "total": 100,
            "total_pages": 10
        }
    }
}
```

#### 错误响应格式

```json
{
    "success": false,  // 失败标志
    "code": 4001,      // 错误码
    "message": "权限不足",  // 错误消息
    "data": null,      // 通常为null
    "meta": {
        "timestamp": "2025-04-15T05:27:16.209460+00:00",
        "exception": "PermissionDenied"  // 异常类型
    }
}
```

### 3.2 认证与授权

#### 认证机制

系统使用JWT（JSON Web Token）进行认证，认证流程如下：

1. 用户通过登录API获取JWT令牌
2. 所有后续请求在HTTP头部包含令牌：`Authorization: Bearer {token}`
3. 令牌包含用户ID、角色和租户信息
4. 令牌有效期为24小时，可通过刷新令牌API延长

#### 登录API

```
POST /api/v1/auth/login/
```

请求体：
```json
{
    "username": "admin",
    "password": "secure_password"
}
```

成功响应：
```json
{
    "success": true,
    "code": 2000,
    "message": "登录成功",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "is_admin": true,
            "is_super_admin": true,
            "tenant_id": null
        }
    },
    "meta": {
        "timestamp": "2025-04-15T05:27:16.209460+00:00"
    }
}
```

#### 令牌刷新API

```
POST /api/v1/auth/refresh/
```

请求体：
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 权限控制

系统权限基于以下几个维度：

1. **用户角色**：超级管理员、租户管理员、普通用户
2. **资源所有权**：是否是资源的创建者或拥有者
3. **租户权限**：是否属于同一租户
4. **操作类型**：读取、创建、更新、删除等

### 3.3 用户管理API

#### 获取当前用户信息

```
GET /api/v1/users/me/
```

#### 用户注册

```
POST /api/v1/users/register/
```

请求体：
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "New",
    "last_name": "User",
    "phone": "1234567890"
}
```

#### 修改用户信息

```
PUT /api/v1/users/{user_id}/
```

请求体：
```json
{
    "first_name": "Updated",
    "last_name": "Name",
    "phone": "9876543210"
}
```

#### 更改密码

```
POST /api/v1/users/change-password/
```

请求体：
```json
{
    "old_password": "current_password",
    "new_password": "new_secure_password",
    "new_password_confirm": "new_secure_password"
}
```

### 3.4 超级用户管理API

#### 创建超级管理员

```
POST /api/v1/users/super-admin/create/
```

请求体：
```json
{
    "username": "new_super_admin",
    "email": "super_admin@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "Super",
    "last_name": "Admin"
}
```

注意：该API只能由现有超级管理员调用。

#### 授予超级管理员权限

```
POST /api/v1/users/{user_id}/grant-super-admin/
```

请求体：
```json
{
    "confirm": true
}
```

#### 撤销超级管理员权限

```
POST /api/v1/users/{user_id}/revoke-super-admin/
```

请求体：
```json
{
    "confirm": true
}
```

### 3.5 租户管理API

#### 创建租户

```
POST /api/v1/tenants/
```

请求体：
```json
{
    "name": "新租户",
    "quota": {
        "max_users": 20,
        "max_admins": 3,
        "max_storage_mb": 2048,
        "max_products": 200
    }
}
```

#### 获取租户列表

```
GET /api/v1/tenants/
```

查询参数：
- `page`：页码，默认为1
- `page_size`：每页记录数，默认为10
- `search`：按名称搜索
- `status`：按状态筛选（active/suspended/deleted）

#### 获取租户详情

```
GET /api/v1/tenants/{tenant_id}/
```

#### 更新租户信息

```
PUT /api/v1/tenants/{tenant_id}/
```

请求体：
```json
{
    "name": "更新的租户名称",
    "status": "active"
}
```

#### 删除租户（软删除）

```
DELETE /api/v1/tenants/{tenant_id}/
```

### 3.6 租户用户API

#### 创建租户用户

```
POST /api/v1/tenants/{tenant_id}/users/
```

请求体：
```json
{
    "username": "tenant_user",
    "email": "user@tenant.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "Tenant",
    "last_name": "User",
    "is_admin": false
}
```

#### 获取租户用户列表

```
GET /api/v1/tenants/{tenant_id}/users/
```

查询参数：
- `page`：页码，默认为1
- `page_size`：每页记录数，默认为10
- `search`：按用户名或邮箱搜索
- `is_admin`：按管理员状态筛选（true/false）

#### 为用户分配租户

```
POST /api/v1/users/tools/assign-tenant/
```

请求体：
```json
{
    "user_id": 123,
    "tenant_id": 456
}
```

#### 更改用户角色

```
POST /api/v1/tenants/{tenant_id}/users/{user_id}/change-role/
```

请求体：
```json
{
    "is_admin": true
}
```

### 3.7 配额管理API

#### 获取租户配额信息

```
GET /api/v1/tenants/{tenant_id}/quota/
```

#### 更新租户配额

```
PUT /api/v1/tenants/{tenant_id}/quota/
```

请求体：
```json
{
    "max_users": 30,
    "max_admins": 5,
    "max_storage_mb": 5120,
    "max_products": 300
}
```

#### 获取配额使用情况

```
GET /api/v1/tenants/{tenant_id}/quota/usage/
```

响应示例：
```json
{
    "success": true,
    "code": 2000,
    "message": "获取成功",
    "data": {
        "users": {
            "current": 8,
            "max": 20,
            "percentage": 40
        },
        "admins": {
            "current": 2,
            "max": 3,
            "percentage": 66.7
        },
        "storage": {
            "current_mb": 512,
            "max_mb": 2048,
            "percentage": 25
        },
        "products": {
            "current": 45,
            "max": 200,
            "percentage": 22.5
        }
    },
    "meta": {
        "timestamp": "2025-04-15T05:27:16.209460+00:00"
    }
}
```

## 4. 部署与配置

### 4.1 环境要求

- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+
- PostgreSQL 12+
- Redis 6+

### 4.2 安装步骤

1. 克隆仓库：`git clone https://github.com/your-repo/multi-tenant-user-management.git`
2. 安装依赖：`pip install -r requirements.txt`
3. 迁移数据库：`python manage.py migrate`
4. 创建超级管理员：`python manage.py createsuperuser`
5. 启动开发服务器：`python manage.py runserver`

### 4.3 配置选项

- `DEBUG`：调试模式，默认为`False`
- `SECRET_KEY`：安全密钥，默认为随机生成的值
- `DATABASES`：数据库配置，默认为PostgreSQL
- `REDIS`：Redis配置，默认为本地Redis

### 4.4 数据库迁移

- 使用`python manage.py makemigrations`生成迁移文件
- 使用`python manage.py migrate`应用迁移

## 5. 测试与质量保证

### 5.1 测试策略

- 单元测试：使用Django内置的测试框架
- 集成测试：使用Pytest和Django的测试客户端
- UI测试：使用Selenium和Pytest

### 5.2 自动化测试

- 使用GitHub Actions或其他CI/CD工具自动运行测试
- 使用Codecov或其他代码覆盖率工具监测测试覆盖率

### 5.3 测试用例说明

- 单元测试：测试模型、视图和服务的正确性
- 集成测试：测试API和UI的正确性
- UI测试：测试UI的正确性和用户体验

### 5.4 如何运行测试

- 使用`python manage.py test`运行单元测试
- 使用`pytest`运行集成测试和UI测试

## 6. 使用示例与最佳实践

### 6.1 系统初始化

- 创建超级管理员
- 配置系统设置

### 6.2 超级用户创建与管理

超级用户（Super Admin）是系统中拥有最高权限的用户角色，可以管理所有租户和用户。创建和管理超级用户有多种方式：

#### 6.2.1 通过命令行创建初始超级用户

Django内置的`createsuperuser`命令是创建系统第一个超级用户的推荐方式：

```bash
# 创建超级用户（交互式）
python manage.py createsuperuser

# 非交互式创建（适用于自动化脚本）
python manage.py createsuperuser --username=admin --email=admin@example.com --noinput
```

随后，需要通过Django管理后台设置用户的`is_super_admin`标志为`True`：

1. 访问管理后台：`http://yoursite/admin/`
2. 登录刚创建的超级用户账号
3. 导航到用户列表
4. 编辑用户并勾选`is_super_admin`选项
5. 保存更改

#### 6.2.2 通过API创建超级用户

只有现有的超级用户才能通过API创建新的超级用户：

```
POST /api/v1/users/super-admin/create/
```

请求体：
```json
{
    "username": "new_super_admin",
    "email": "super_admin@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "Super",
    "last_name": "Admin"
}
```

创建成功后，响应将包含新超级用户的详细信息：

```json
{
    "success": true,
    "code": 2000,
    "message": "超级管理员创建成功",
    "data": {
        "id": 123,
        "username": "new_super_admin",
        "email": "super_admin@example.com",
        "first_name": "Super",
        "last_name": "Admin",
        "is_super_admin": true,
        "tenant_id": null
    },
    "meta": {
        "timestamp": "2025-04-15T05:27:16.209460+00:00"
    }
}
```

#### 6.2.3 将现有用户提升为超级用户

可以通过API将现有用户提升为超级用户：

```
POST /api/v1/users/{user_id}/grant-super-admin/
```

请求体：
```json
{
    "confirm": true
}
```

注意事项：
- 此操作需要确认字段`confirm`设置为`true`，以防止误操作
- 只有当前超级用户才能执行此操作
- 被提升的用户将自动解除与任何租户的关联，因为超级用户不属于任何特定租户

#### 6.2.4 撤销超级用户权限

如果需要，可以撤销超级用户的权限：

```
POST /api/v1/users/{user_id}/revoke-super-admin/
```

请求体：
```json
{
    "confirm": true,
    "assign_to_tenant_id": 456  // 可选，撤销后分配到指定租户
}
```

#### 6.2.5 超级用户权限与安全注意事项

1. **最小权限原则**：
   - 只授予真正需要的用户超级管理员权限
   - 定期审核超级管理员列表，确保权限分配合理

2. **操作审计**：
   - 系统会记录所有超级管理员的关键操作
   - 这些日志可通过管理后台查看

3. **密码策略**：
   - 超级用户应使用强密码（至少12位，包含大小写字母、数字和特殊字符）
   - 建议启用双因素认证

4. **访问限制**：
   - 考虑限制超级用户的API访问来源IP
   - 实施登录尝试限制，防止暴力破解

5. **紧急处理**：
   - 确保至少有两名超级用户，防止单点故障
   - 制定紧急响应计划，应对超级用户账号被盗用的情况

### 6.3 常见场景

- 用户注册和登录
- 租户创建和管理
- 配额管理

### 6.4 集成示例

- 使用Django的内置认证系统
- 使用第三方认证服务（如OAuth）

### 6.5 性能优化

- 使用缓存（如Redis）
- 使用CDN
- 优化数据库查询

## 7. 故障排除与FAQ

### 7.1 常见问题

- 如何解决登录问题
- 如何解决权限问题
- 如何解决数据库连接问题

### 7.2 错误码解释

- 4001：权限不足
- 4002：登录失败
- 5001：数据库连接错误

### 7.3 日志说明

- 使用Django的内置日志系统
- 使用第三方日志服务（如Splunk）

## 8. 扩展与定制

### 8.1 扩展点

- 使用Django的内置扩展点（如中间件）
- 使用第三方扩展点（如Django REST Framework的扩展点）

### 8.2 自定义建议

- 使用Django的内置自定义选项（如模板标签）
- 使用第三方自定义选项（如Django REST Framework的自定义选项）
