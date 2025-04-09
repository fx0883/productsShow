# 商品管理系统 - API接口规范

## 1. API概述

商品管理系统采用RESTful API设计风格，使用JSON作为数据交换格式，JWT用于身份验证。所有API遵循以下设计原则：

- 使用HTTP动词表示操作（GET、POST、PUT、DELETE等）
- 使用名词复数形式作为资源标识
- 使用HTTP状态码表示请求结果
- 统一的响应格式
- 支持分页、过滤、排序和字段选择
- 支持CORS（跨域资源共享）

## 2. 基础URL

所有API请求都使用以下基础URL：

```
https://{domain}/api/v1
```

其中，`{domain}`是系统域名，`v1`表示API版本号。

## 3. 认证与授权

### 3.1 认证机制

系统使用基于JWT（JSON Web Token）的认证机制：

1. 客户端通过`/api/v1/auth/login`获取令牌
2. 客户端在后续请求中通过Authorization头部包含令牌
3. 令牌有效期为24小时，可通过`/api/v1/auth/refresh`刷新

### 3.2 请求头部

认证请求需要包含以下HTTP头：

```
Authorization: Bearer {token}
```

### 3.3 认证相关接口

#### 登录接口

- **URL**: `/api/v1/auth/login`
- **方法**: POST
- **请求参数**:

```json
{
  "username": "user_name",
  "password": "user_password"
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "user_name",
      "email": "user@example.com",
      "is_admin": true,
      "is_member": true
    }
  }
}
```

#### 刷新令牌

- **URL**: `/api/v1/auth/refresh`
- **方法**: POST
- **请求参数**:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

#### 注销

- **URL**: `/api/v1/auth/logout`
- **方法**: POST
- **请求头**: 需要包含Authorization头部
- **响应**:

```json
{
  "status": "success",
  "message": "成功注销"
}
```

## 4. 全局响应格式

所有API响应遵循以下格式：

### 4.1 成功响应

```json
{
  "status": "success",
  "data": {
    // 返回的数据
  },
  "message": "操作成功"
}
```

对于列表类资源，包含分页信息：

```json
{
  "status": "success",
  "data": [
    // 数据列表
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 5,
    "total_items": 47
  }
}
```

### 4.2 错误响应

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "错误描述",
  "details": {
    // 详细错误信息，如表单验证错误
  }
}
```

### 4.3 常见HTTP状态码

- **200 OK**: 请求成功
- **201 Created**: 资源创建成功
- **204 No Content**: 请求成功，无返回内容
- **400 Bad Request**: 请求参数错误
- **401 Unauthorized**: 未认证或认证失败
- **403 Forbidden**: 权限不足
- **404 Not Found**: 资源不存在
- **422 Unprocessable Entity**: 请求格式正确但含有语义错误
- **500 Internal Server Error**: 服务器内部错误

## 5. 用户管理API

### 5.1 获取用户列表（仅管理员）

- **URL**: `/api/v1/users`
- **方法**: GET
- **权限**: 管理员
- **查询参数**:
  - `page`: 页码，默认1
  - `per_page`: 每页数量，默认10
  - `sort`: 排序字段，如`created_at`
  - `order`: 排序方向，`asc`或`desc`
  - `search`: 搜索关键词
  - `role`: 用户角色过滤，`admin`或`member`
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "is_admin": true,
      "is_member": false,
      "phone": "13800138000",
      "created_at": "2025-01-01T00:00:00Z",
      "last_login": "2025-04-01T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 1,
    "total_items": 1
  }
}
```

### 5.2 获取单个用户信息

- **URL**: `/api/v1/users/{id}`
- **方法**: GET
- **权限**: 管理员可查看任意用户，普通用户只能查看自己
- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true,
    "is_member": false,
    "phone": "13800138000",
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-04-01T10:00:00Z",
    "profile": {
      "preferred_language": "zh-cn",
      "date_format": "YYYY-MM-DD"
    }
  }
}
```

### 5.3 创建用户（仅管理员）

- **URL**: `/api/v1/users`
- **方法**: POST
- **权限**: 管理员
- **请求参数**:

```json
{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password",
  "is_admin": false,
  "is_member": true,
  "phone": "13900139000",
  "profile": {
    "preferred_language": "zh-cn",
    "date_format": "YYYY-MM-DD"
  }
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "username": "new_user",
    "email": "user@example.com",
    "is_admin": false,
    "is_member": true,
    "phone": "13900139000",
    "created_at": "2025-04-08T16:00:00Z"
  },
  "message": "用户创建成功"
}
```

### 5.4 更新用户信息

- **URL**: `/api/v1/users/{id}`
- **方法**: PUT
- **权限**: 管理员可更新任意用户，普通用户只能更新自己
- **请求参数**:

```json
{
  "email": "updated_email@example.com",
  "phone": "13911139111",
  "profile": {
    "preferred_language": "en-us"
  }
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "username": "new_user",
    "email": "updated_email@example.com",
    "phone": "13911139111",
    "updated_at": "2025-04-08T16:30:00Z"
  },
  "message": "用户信息更新成功"
}
```

### 5.5 删除用户（仅管理员）

- **URL**: `/api/v1/users/{id}`
- **方法**: DELETE
- **权限**: 管理员
- **响应**:

```json
{
  "status": "success",
  "message": "用户删除成功"
}
```

### 5.6 修改密码

- **URL**: `/api/v1/users/{id}/password`
- **方法**: PUT
- **权限**: 管理员可修改任意用户，普通用户只能修改自己
- **请求参数**:

```json
{
  "current_password": "old_password", // 普通用户修改自己密码时需要
  "new_password": "new_secure_password"
}
```

- **响应**:

```json
{
  "status": "success",
  "message": "密码修改成功"
}
```

## 6. 商品管理API

### 6.1 获取商品列表

- **URL**: `/api/v1/products`
- **方法**: GET
- **权限**: 所有认证用户
- **查询参数**:
  - `page`: 页码，默认1
  - `per_page`: 每页数量，默认10
  - `sort`: 排序字段，如`created_at`, `name`, `price`
  - `order`: 排序方向，`asc`或`desc`
  - `search`: 搜索关键词（在名称、描述和SKU中搜索）
  - `type`: 商品类型，`simple`或`variable`
  - `status`: 商品状态，`draft`，`published`或`trash`
  - `category`: 分类ID
  - `min_price`: 最低价格
  - `max_price`: 最高价格
  - `featured`: 是否精选，`true`或`false`
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "示例商品",
      "slug": "example-product",
      "sku": "PRD001",
      "type": "simple",
      "status": "published",
      "featured": false,
      "short_description": "这是一个示例商品",
      "price": 99.99,
      "regular_price": 129.99,
      "sale_price": 99.99,
      "stock_quantity": 100,
      "categories": [
        {
          "id": 1,
          "name": "示例分类",
          "slug": "example-category"
        }
      ],
      "image": "https://example.com/images/product1.jpg",
      "created_at": "2025-03-15T00:00:00Z",
      "updated_at": "2025-04-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 5,
    "total_items": 48
  }
}
```

### 6.2 获取单个商品详情

- **URL**: `/api/v1/products/{id}`
- **方法**: GET
- **权限**: 所有认证用户
- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "示例商品",
    "slug": "example-product",
    "sku": "PRD001",
    "type": "variable",
    "status": "published",
    "featured": false,
    "description": "这是一个完整的商品描述...",
    "short_description": "这是一个示例商品",
    "price": null,
    "regular_price": null,
    "sale_price": null,
    "categories": [
      {
        "id": 1,
        "name": "示例分类",
        "slug": "example-category"
      }
    ],
    "images": [
      {
        "id": 1,
        "image": "https://example.com/images/product1_1.jpg",
        "alt_text": "商品主图",
        "is_featured": true
      },
      {
        "id": 2,
        "image": "https://example.com/images/product1_2.jpg",
        "alt_text": "商品细节图",
        "is_featured": false
      }
    ],
    "attributes": [
      {
        "id": 1,
        "name": "颜色",
        "values": ["红色", "蓝色", "黑色"]
      },
      {
        "id": 2,
        "name": "尺寸",
        "values": ["S", "M", "L", "XL"]
      }
    ],
    "variations": [
      {
        "id": 1,
        "sku": "PRD001-RED-M",
        "price": 99.99,
        "regular_price": 129.99,
        "sale_price": 99.99,
        "stock_quantity": 20,
        "attributes": [
          {
            "name": "颜色",
            "value": "红色"
          },
          {
            "name": "尺寸",
            "value": "M"
          }
        ]
      },
      {
        "id": 2,
        "sku": "PRD001-BLUE-L",
        "price": 99.99,
        "regular_price": 129.99,
        "sale_price": 99.99,
        "stock_quantity": 15,
        "attributes": [
          {
            "name": "颜色",
            "value": "蓝色"
          },
          {
            "name": "尺寸",
            "value": "L"
          }
        ]
      }
    ],
    "created_at": "2025-03-15T00:00:00Z",
    "updated_at": "2025-04-01T00:00:00Z"
  }
}
```

### 6.3 创建商品

- **URL**: `/api/v1/products`
- **方法**: POST
- **权限**: 管理员
- **请求参数**:

```json
{
  "name": "新商品",
  "slug": "new-product",
  "sku": "PRD002",
  "type": "simple",
  "status": "draft",
  "featured": false,
  "description": "这是一个新商品的详细描述...",
  "short_description": "这是一个新商品",
  "regular_price": 199.99,
  "sale_price": 159.99,
  "stock_quantity": 50,
  "categories": [1, 2],
  "images": [
    {
      "image": "https://example.com/images/new_product1.jpg",
      "alt_text": "新商品图片",
      "is_featured": true
    }
  ]
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "name": "新商品",
    "slug": "new-product",
    "sku": "PRD002",
    "type": "simple",
    "status": "draft",
    "featured": false,
    "short_description": "这是一个新商品",
    "regular_price": 199.99,
    "sale_price": 159.99,
    "price": 159.99,
    "stock_quantity": 50,
    "created_at": "2025-04-08T17:00:00Z"
  },
  "message": "商品创建成功"
}
```

### 6.4 更新商品

- **URL**: `/api/v1/products/{id}`
- **方法**: PUT
- **权限**: 管理员
- **请求参数**:

```json
{
  "name": "更新的商品名称",
  "description": "更新的商品描述...",
  "status": "published",
  "regular_price": 189.99,
  "sale_price": 149.99,
  "stock_quantity": 45
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "name": "更新的商品名称",
    "status": "published",
    "regular_price": 189.99,
    "sale_price": 149.99,
    "price": 149.99,
    "stock_quantity": 45,
    "updated_at": "2025-04-08T17:30:00Z"
  },
  "message": "商品更新成功"
}
```

### 6.5 删除商品

- **URL**: `/api/v1/products/{id}`
- **方法**: DELETE
- **权限**: 管理员
- **响应**:

```json
{
  "status": "success",
  "message": "商品删除成功"
}
```

### 6.6 批量处理商品

- **URL**: `/api/v1/products/batch`
- **方法**: POST
- **权限**: 管理员
- **请求参数**:

```json
{
  "action": "delete|update|trash|restore",
  "ids": [3, 4, 5],
  "data": {
    // 当action为update时需要提供，更新的字段
    "status": "published",
    "featured": true
  }
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "affected": 3
  },
  "message": "批量操作成功"
}
```

### 6.7 获取商品变体

- **URL**: `/api/v1/products/{product_id}/variations`
- **方法**: GET
- **权限**: 所有认证用户
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "sku": "PRD001-RED-M",
      "price": 99.99,
      "regular_price": 129.99,
      "sale_price": 99.99,
      "stock_quantity": 20,
      "attributes": [
        {
          "name": "颜色",
          "value": "红色"
        },
        {
          "name": "尺寸",
          "value": "M"
        }
      ]
    }
  ]
}
```

### 6.8 创建商品变体

- **URL**: `/api/v1/products/{product_id}/variations`
- **方法**: POST
- **权限**: 管理员
- **请求参数**:

```json
{
  "sku": "PRD001-BLACK-XL",
  "regular_price": 129.99,
  "sale_price": 99.99,
  "stock_quantity": 10,
  "attributes": [
    {
      "attribute_id": 1,
      "value_id": 3 // 黑色的ID
    },
    {
      "attribute_id": 2,
      "value_id": 4 // XL的ID
    }
  ]
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 3,
    "sku": "PRD001-BLACK-XL",
    "price": 99.99,
    "regular_price": 129.99,
    "sale_price": 99.99,
    "stock_quantity": 10,
    "created_at": "2025-04-08T18:00:00Z"
  },
  "message": "商品变体创建成功"
}
```

## 7. 分类管理API

### 7.1 获取分类列表

- **URL**: `/api/v1/categories`
- **方法**: GET
- **权限**: 所有认证用户
- **查询参数**:
  - `page`: 页码，默认1
  - `per_page`: 每页数量，默认10
  - `parent`: 父分类ID，获取特定父分类下的子分类
  - `search`: 搜索关键词
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "电子产品",
      "slug": "electronics",
      "description": "电子产品分类",
      "parent": null,
      "image": "https://example.com/images/categories/electronics.jpg",
      "count": 15, // 该分类下的商品数量
      "children": [
        {
          "id": 2,
          "name": "手机",
          "slug": "phones",
          "parent": 1,
          "count": 8
        },
        {
          "id": 3,
          "name": "电脑",
          "slug": "computers",
          "parent": 1,
          "count": 7
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 1,
    "total_items": 1
  }
}
```

### 7.2 获取单个分类详情

- **URL**: `/api/v1/categories/{id}`
- **方法**: GET
- **权限**: 所有认证用户
- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "电子产品",
    "slug": "electronics",
    "description": "电子产品分类详细描述...",
    "parent": null,
    "image": "https://example.com/images/categories/electronics.jpg",
    "count": 15,
    "children": [
      {
        "id": 2,
        "name": "手机",
        "slug": "phones",
        "parent": 1,
        "count": 8
      },
      {
        "id": 3,
        "name": "电脑",
        "slug": "computers",
        "parent": 1,
        "count": 7
      }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-03-01T00:00:00Z"
  }
}
```

### 7.3 创建分类

- **URL**: `/api/v1/categories`
- **方法**: POST
- **权限**: 管理员
- **请求参数**:

```json
{
  "name": "智能家居",
  "slug": "smart-home",
  "description": "智能家居产品分类",
  "parent": 1, // 可选，父分类ID
  "image": "https://example.com/images/categories/smart-home.jpg"
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 4,
    "name": "智能家居",
    "slug": "smart-home",
    "description": "智能家居产品分类",
    "parent": 1,
    "image": "https://example.com/images/categories/smart-home.jpg",
    "created_at": "2025-04-08T18:30:00Z"
  },
  "message": "分类创建成功"
}
```

### 7.4 更新分类

- **URL**: `/api/v1/categories/{id}`
- **方法**: PUT
- **权限**: 管理员
- **请求参数**:

```json
{
  "name": "智能家居设备",
  "description": "更新的智能家居产品分类描述"
}
```

- **响应**:

```json
{
  "status": "success",
  "data": {
    "id": 4,
    "name": "智能家居设备",
    "slug": "smart-home",
    "description": "更新的智能家居产品分类描述",
    "parent": 1,
    "updated_at": "2025-04-08T19:00:00Z"
  },
  "message": "分类更新成功"
}
```

### 7.5 删除分类

- **URL**: `/api/v1/categories/{id}`
- **方法**: DELETE
- **权限**: 管理员
- **响应**:

```json
{
  "status": "success",
  "message": "分类删除成功"
}
```
