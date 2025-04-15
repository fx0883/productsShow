# 多租户用户管理系统文档

## 目录

1. [系统概述](#1-系统概述)
2. [数据结构设计](#2-数据结构设计)
3. [系统架构设计](#3-系统架构设计)
4. [API接口文档](#4-api接口文档)
5. [用户角色与权限](#5-用户角色与权限)
6. [系统管理指南](#6-系统管理指南)

## 1. 系统概述

### 1.1 设计目标

多租户用户管理系统旨在提供一个可扩展的基础架构，支持在单一应用实例中管理多个互相隔离的租户（组织或客户）。系统主要目标包括：

- **数据隔离**：确保不同租户之间的数据完全隔离，防止跨租户数据访问
- **资源管理**：为每个租户提供资源配额管理，控制其资源使用量
- **灵活授权**：提供多级权限管理，包括超级管理员、租户管理员和普通用户角色
- **自助管理**：允许租户管理员自主管理其租户内的用户和数据

### 1.2 核心功能

- 租户创建与管理
- 租户级别用户管理
- 资源配额设置与监控
- 跨租户权限管理
- 租户使用统计报告

### 1.3 技术栈

- **后端框架**：Django, Django REST Framework
- **数据库**：MySQL
- **认证方式**：JWT (JSON Web Token)
- **API文档**：Swagger/OpenAPI (drf-spectacular)

## 2. 数据结构设计

### 2.1 实体关系图

```
+-------------+       +---------------+
|   Tenant    |<------| TenantQuota   |
+-------------+       +---------------+
      ^
      |
      |
+-------------+
|    User     |
+-------------+
      ^
      |
      |
+-------------+       +---------------+
| BaseModel   |<------| 各业务模型    |
+-------------+       +---------------+
```

### 2.2 核心数据模型

#### 2.2.1 Tenant（租户）模型

```python
class Tenant(models.Model):
    """
    租户模型，用于隔离不同租户的数据
    """
    STATUS_CHOICES = (
        ('active', '活跃'),
        ('suspended', '暂停'),
        ('deleted', '已删除'),
    )
    
    name = models.CharField(_("租户名称"), max_length=100, unique=True)
    status = models.CharField(_("状态"), max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
```

租户是整个多租户系统的核心实体，代表一个独立的组织或客户。每个租户拥有自己的用户和数据。

#### 2.2.2 User（用户）模型

```python
class User(AbstractUser):
    """
    自定义用户模型
    """
    # 租户关联字段
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, related_name="users")
    
    # 用户角色字段
    is_admin = models.BooleanField(_("是否管理员"), default=False)
    is_member = models.BooleanField(_("是否成员"), default=False)
    is_super_admin = models.BooleanField(_("是否超级管理员"), default=False)
    
    # 其他用户信息字段
    phone = models.CharField(_("手机号"), max_length=11, null=True, blank=True)
    email = models.EmailField(_("邮箱"), unique=True)
    nick_name = models.CharField(_("昵称"), max_length=30, null=True, blank=True)
    avatar = models.CharField(_("头像"), max_length=200, default="")
```

用户模型扩展了Django的AbstractUser，增加了租户关联和多级角色支持。

#### 2.2.3 TenantQuota（租户配额）模型

```python
class TenantQuota(models.Model):
    """
    租户配额模型，用于限制租户的资源使用
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='quota',
        verbose_name=_('租户')
    )
    max_users = models.IntegerField(_('最大用户数'), default=10)
    max_admins = models.IntegerField(_('最大管理员数'), default=2)
    max_storage_mb = models.IntegerField(_('最大存储空间(MB)'), default=1024)  # 默认1GB
    max_products = models.IntegerField(_('最大产品数'), default=100)
    
    # 跟踪当前使用情况
    current_storage_used_mb = models.IntegerField(_('当前已用存储空间(MB)'), default=0)
```

租户配额模型为每个租户定义资源使用限制，并跟踪资源的实际使用情况。

#### 2.2.4 BaseModel（基础模型）

```python
class BaseModel(models.Model):
    """
    基础模型，所有需要租户隔离的模型都应该继承此模型
    """
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        verbose_name=_("租户"),
        related_name="%(class)s_set",
        db_index=True,
        null=True
    )
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True, null=True)
    is_deleted = models.BooleanField(_("是否删除"), default=False)
    
    # 默认管理器 - 按租户过滤
    objects = TenantManager()
    
    # 原始管理器 - 不过滤，用于管理员访问所有数据
    original_objects = models.Manager()
    
    class Meta:
        abstract = True
```

BaseModel是一个抽象模型，所有需要租户隔离的业务模型都应继承此模型。它提供了租户关联、创建/更新时间字段，以及基于租户自动过滤的管理器。

### 2.3 数据关联关系

- **租户-用户**：一对多关系，一个租户可以拥有多个用户
- **租户-配额**：一对一关系，每个租户有一个对应的配额设置
- **租户-业务数据**：通过BaseModel实现一对多关系，所有业务数据都关联到特定租户

## 3. 系统架构设计

### 3.1 整体架构

我们的多租户系统采用共享数据库、共享架构(Shared Database, Shared Schema)的多租户架构模式，所有租户的数据存储在同一个数据库中，通过租户ID字段实现数据隔离。

### 3.2 租户中间件

系统使用`TenantMiddleware`中间件来管理租户上下文：

```python
class TenantMiddleware(MiddlewareMixin):
    """
    租户中间件，用于设置请求的租户上下文
    """
    def process_request(self, request):
        """
        处理请求，设置当前租户
        """
        # 清除之前的租户上下文
        set_current_tenant(None)
        
        # 未登录用户没有租户上下文
        if not request.user.is_authenticated:
            return None
        
        # 获取用户关联的租户
        tenant = getattr(request.user, 'tenant', None)
        
        # 设置当前线程的租户上下文
        if tenant:
            set_current_tenant(tenant)
        
        return None
```

中间件从当前认证用户中获取租户信息，并将其存储在线程本地存储中，后续数据库查询将自动应用此租户上下文。

### 3.3 查询过滤

`TenantManager`是一个自定义的模型管理器，它自动根据当前租户上下文过滤查询结果：

```python
class TenantManager(models.Manager):
    """
    租户模型管理器，自动根据当前租户过滤查询集
    """
    def get_queryset(self):
        """
        重写查询集方法，自动按当前租户过滤
        """
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            # 如果有租户上下文，则过滤结果
            return queryset.filter(tenant=tenant)
        
        # 如果没有租户上下文，返回全部结果（超级管理员场景）
        return queryset
```

### 3.4 权限控制

系统定义了三种主要角色：

- **超级管理员(SuperAdmin)**：可以管理所有租户和用户
- **租户管理员(TenantAdmin)**：可以管理其所属租户内的用户和数据
- **普通用户(Member)**：只能访问所属租户内的数据

权限检查通过自定义权限类实现：

```python
class IsSuperAdminUser(BasePermission):
    """
    检查用户是否是超级管理员
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin)

class IsAdminUser(BasePermission):
    """
    检查用户是否是管理员（包括超级管理员和租户管理员）
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_super_admin)
        )
```

## 4. API接口文档

### 4.1 认证机制

系统使用JWT(JSON Web Token)进行API认证：

- 用户通过`/api/v1/users/login/`接口获取token
- 后续请求在Header中添加`Authorization: Bearer {token}`进行身份验证

### 4.2 租户管理API

#### 4.2.1 租户列表和创建

- **GET /api/v1/common/tenants/**
  - 权限：超级管理员
  - 功能：获取所有租户列表
  
- **POST /api/v1/common/tenants/**
  - 权限：超级管理员
  - 功能：创建新租户
  - 请求体示例：
    ```json
    {
        "name": "新租户",
        "status": "active"
    }
    ```

#### 4.2.2 租户详情操作

- **GET /api/v1/common/tenants/{tenant_id}/**
  - 权限：超级管理员
  - 功能：获取指定租户的详细信息，包括配额和使用情况
  
- **PUT /api/v1/common/tenants/{tenant_id}/**
  - 权限：超级管理员
  - 功能：更新租户信息
  
- **DELETE /api/v1/common/tenants/{tenant_id}/**
  - 权限：超级管理员
  - 功能：删除租户（软删除）

### 4.3 租户用户管理API

- **GET /api/v1/common/tenants/users/**
  - 权限：超级管理员或租户管理员
  - 功能：获取租户用户列表
  - 查询参数：
    - `tenant_id`：租户ID（超级管理员必填）
    - `page`：页码
    - `page_size`：每页数量
    - `search`：搜索关键词

- **POST /api/v1/users/tenant/users/create/**
  - 权限：租户管理员
  - 功能：在当前租户中创建新用户
  - 请求体示例：
    ```json
    {
        "username": "tenant_user1",
        "email": "tenant_user1@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "is_admin": false,
        "is_member": true
    }
    ```

### 4.4 租户配额管理API

- **GET /api/v1/common/tenants/quota/**
  - 权限：超级管理员
  - 功能：获取指定租户的配额信息
  - 查询参数：
    - `tenant_id`：租户ID

- **PUT /api/v1/common/tenants/quota/**
  - 权限：超级管理员
  - 功能：更新租户配额设置
  - 请求体示例：
    ```json
    {
        "tenant": 1,
        "max_users": 20,
        "max_admins": 5,
        "max_storage_mb": 2048,
        "max_products": 200
    }
    ```

## 5. 用户角色与权限

### 5.1 角色定义

系统定义了三个主要角色，通过用户模型中的布尔标志字段实现：

1. **超级管理员(SuperAdmin)**：`is_super_admin = True`
   - 可跨租户访问所有数据
   - 管理所有租户和用户
   - 设置租户配额

2. **租户管理员(TenantAdmin)**：`is_admin = True`
   - 管理其所属租户内的用户
   - 查看租户内的所有数据
   - 不能跨租户访问数据

3. **普通用户(Member)**：`is_member = True`
   - 只能访问所属租户内的授权数据
   - 不能管理其他用户

### 5.2 权限矩阵

| 操作               | 超级管理员 | 租户管理员 | 普通用户 |
|--------------------|------------|------------|----------|
| 创建租户           | ✓          | ✗          | ✗        |
| 管理租户           | ✓          | ✗          | ✗        |
| 设置租户配额       | ✓          | ✗          | ✗        |
| 查看所有租户       | ✓          | ✗          | ✗        |
| 创建租户用户       | ✓          | ✓ (本租户)  | ✗        |
| 管理租户用户       | ✓          | ✓ (本租户)  | ✗        |
| 查看租户用户列表   | ✓          | ✓ (本租户)  | ✗        |
| 访问业务数据       | ✓ (全部)   | ✓ (本租户)  | ✓ (本租户) |

## 6. 系统管理指南

### 6.1 创建超级管理员

系统提供了专门的管理命令来创建超级管理员：

```bash
python manage.py create_super_admin --username admin --password password --email admin@example.com [--nick_name 昵称] [--tenant 租户名]
```

参数说明：
- `--username`：用户名（必填）
- `--password`：密码（必填）
- `--email`：电子邮箱（必填）
- `--nick_name`：昵称（可选）
- `--phone`：手机号码（可选）
- `--tenant`：关联租户名称（可选，如不指定则使用"默认租户"）

### 6.2 租户管理流程

1. **创建租户**：超级管理员通过API创建新租户
2. **设置配额**：为新租户设置资源配额
3. **创建租户管理员**：创建该租户的管理员账户
4. **用户管理**：租户管理员可以创建和管理租户内的普通用户

### 6.3 配额监控

系统会自动跟踪租户的资源使用情况：

- 用户数量：系统统计租户关联的用户数
- 管理员数量：统计租户内的管理员用户数
- 存储使用量：跟踪上传文件的存储空间使用
- 产品数量：统计租户创建的产品数

当资源使用超过配额限制时，系统会拒绝相关操作。

### 6.4 系统维护

- **定期更新配额使用情况**：可通过定时任务定期更新租户的资源使用统计
- **租户停用**：可通过设置租户状态为"suspended"来临时停用租户
- **租户删除**：使用软删除机制，将租户状态设置为"deleted"
