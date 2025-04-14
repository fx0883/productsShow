# ProductsShow API 文档

## 概述

ProductsShow API 是一套基于 RESTful 架构的接口，用于产品管理系统的前后端交互。本文档描述了 API 的使用方法、认证机制以及各个端点的详细信息。

## API 访问

### 基础URL

所有 API 请求的基础 URL 为：

```
http://your-domain.com/api/v1/
```

开发环境中，通常为：

```
http://localhost:8000/api/v1/
```

### API 文档界面

我们提供了多种格式的 API 文档界面：

- **Swagger UI**: `/api/swagger/` - 交互式 API 文档界面，可直接测试 API
- **ReDoc**: `/api/redoc/` - 更适合阅读的 API 文档格式
- **OpenAPI Schema**: `/api/schema/` - 原始的 OpenAPI 规范文档

## 认证机制

### JWT 认证

API 使用 JWT (JSON Web Token) 进行认证。大多数 API 端点需要在请求头中包含有效的访问令牌：

```
Authorization: Bearer {access_token}
```

每个访问令牌有效期为1小时，刷新令牌有效期为7天。

### JWT 认证最佳实践

1. **令牌安全存储**
   - 前端应用应将访问令牌存储在内存中或安全的短期存储中
   - 刷新令牌可以存储在 HttpOnly Cookie 中，以防止 XSS 攻击

2. **令牌刷新策略**
   - 在访问令牌过期前主动刷新，避免用户体验中断
   - 也可以在接收到 401 响应后尝试使用刷新令牌获取新的访问令牌

3. **错误处理**
   - 处理各种认证相关错误：令牌过期、令牌无效、令牌格式错误等
   - 建议在前端统一处理认证错误，并引导用户重新登录

### 时区处理说明

JWT 令牌中的过期时间使用 UTC 时间戳。当处理令牌验证时，系统会自动处理时区转换，确保正确验证令牌的有效性。客户端无需进行特殊的时区处理。

## 获取令牌

通过以下端点获取访问令牌和刷新令牌：

#### 注册

```
POST /api/v1/users/auth/register/
```

请求体示例：
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "phone": "13800138000",
  "password": "Secure@Password123",
  "password_confirm": "Secure@Password123"
}
```

响应示例：
```json
{
  "success": true,
  "code": 201,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 5,
      "username": "testuser",
      "email": "test@example.com",
      "phone": "13800138000",
      "is_admin": false,
      "is_member": true,
      "date_joined": "2025-04-12T14:30:15Z",
      "last_login": null
    },
    "access_token": "eyJ0eXAiOiJKV...",
    "refresh_token": "eyJ0eXAiOiJKV...",
    "token_type": "Bearer"
  },
  "meta": {
    "timestamp": "2025-04-12T14:30:15.163406+00:00"
  }
}
```

#### 登录

```
POST /api/v1/users/auth/login/
```

请求体示例（使用用户名）：
```json
{
  "username": "testuser",
  "password": "Secure@Password123"
}
```

请求体示例（使用邮箱）：
```json
{
  "email": "test@example.com",
  "password": "Secure@Password123"
}
```

响应示例：
```json
{
  "success": true,
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 5,
      "username": "testuser",
      "email": "test@example.com",
      "phone": "13800138000",
      "is_admin": false,
      "is_member": true,
      "date_joined": "2025-04-12T14:30:15Z",
      "last_login": "2025-04-12T14:35:22Z"
    },
    "access_token": "eyJ0eXAiOiJKV...",
    "refresh_token": "eyJ0eXAiOiJKV...",
    "token_type": "Bearer"
  },
  "meta": {
    "timestamp": "2025-04-12T14:35:22.789406+00:00"
  }
}
```

#### 刷新令牌

当访问令牌过期时，使用刷新令牌获取新的访问令牌：

```
POST /api/v1/users/auth/refresh/
```

请求体示例：
```json
{
  "refresh_token": "eyJ0eXAiOiJKV..."
}
```

响应示例：
```json
{
  "success": true,
  "code": 200,
  "message": "令牌刷新成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV...",
    "refresh_token": "eyJ0eXAiOiJKV...",
    "token_type": "Bearer"
  },
  "meta": {
    "timestamp": "2025-04-12T15:30:15.163406+00:00"
  }
}
```

#### 登出

使令牌失效：

```
POST /api/v1/users/auth/logout/
```

请求头：
```
Authorization: Bearer {access_token}
```

响应示例：
```json
{
  "success": true,
  "code": 200,
  "message": "登出成功",
  "data": null,
  "meta": {
    "timestamp": "2025-04-12T15:35:22.789406+00:00"
  }
}
```

## 错误处理

API 使用标准的 HTTP 状态码和统一的错误响应格式：

```json
{
  "success": false,
  "code": 400,
  "message": "错误消息",
  "data": {
    "field1": ["字段错误说明"],
    "field2": ["字段错误说明"]
  },
  "meta": {
    "timestamp": "2025-04-12T16:25:22.789406+00:00",
    "exception": "错误类型"
  }
}
```

### 常见错误码

- 400 - 请求参数错误
- 401 - 未授权（缺少或无效的令牌）
- 403 - 禁止访问（权限不足）
- 404 - 资源不存在
- 500 - 服务器内部错误

### 认证相关错误码

- 20001 - 令牌格式错误
- 20002 - 令牌已过期
- 20003 - 认证失败（详见错误消息）
- 20004 - 无效的刷新令牌

### 错误处理建议

对于前端应用，建议实现以下错误处理策略：

1. **令牌过期（20002）**
   - 尝试使用刷新令牌获取新的访问令牌
   - 如果刷新失败，引导用户重新登录

2. **认证失败（20003）**
   - 清除本地存储的令牌
   - 引导用户重新登录

3. **权限错误（403）**
   - 显示适当的错误消息，说明用户没有权限执行该操作
   - 不要自动登出用户

## API 响应结构

所有 API 响应遵循统一的 JSON 格式：

```json
{
  "success": true/false,         // 请求是否成功
  "code": 200,                   // 状态码
  "message": "操作结果描述",      // 操作结果描述
  "data": { ... },               // 响应数据（可选）
  "meta": {                      // 元数据
    "timestamp": "ISO时间戳",     // 响应时间戳
    ...                          // 其他元数据
  }
}
```
