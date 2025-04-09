# 商品管理系统 - 系统设计概述

## 1. 系统架构

### 1.1 整体架构

商品管理系统采用前后端分离的架构，使用Django + Vue3 + MySQL技术栈：

![系统架构图](https://placeholder-for-architecture-diagram.com)

- **前端**：Vue3开发的单页应用(SPA)，采用扁平化设计风格
- **后端**：Django + Django REST Framework提供API服务
- **数据存储**：MySQL数据库
- **认证**：JWT (JSON Web Token)认证机制
- **部署**：cPanel环境

### 1.2 技术栈详情

#### 后端技术栈
- **Web框架**：Django 4.x
- **API框架**：Django REST Framework
- **ORM**：Django内置ORM
- **认证**：Django REST Framework JWT
- **数据库**：MySQL 8.x
- **多语言支持**：Django内置国际化(i18n)功能
- **文件处理**：Django内置文件处理 + pandas (CSV导出)

#### 前端技术栈
- **框架**：Vue 3.x
- **路由**：Vue Router
- **状态管理**：Vuex/Pinia
- **UI组件库**：Element Plus
- **HTTP客户端**：Axios
- **国际化**：vue-i18n
- **构建工具**：Vite

## 2. 系统模块设计

### 2.1 用户管理模块

用户管理模块负责系统用户的认证和授权。

**主要功能**：
- 用户注册
- 用户登录（JWT认证）
- 用户角色管理（Admin和Member）
- 用户信息管理

**技术实现**：
- 使用Django内置用户系统扩展
- Django REST Framework提供API
- JWT处理无状态认证
- 权限控制基于Django权限系统

### 2.2 商品管理模块

商品管理模块处理商品信息的CRUD操作。

**主要功能**：
- 商品信息管理（添加、编辑、删除）
- 商品分类管理
- 变体产品管理
- 商品导入导出

**技术实现**：
- Django模型设计符合WooCommerce产品结构
- 复杂查询使用Django ORM
- 批量操作通过事务保证数据一致性
- 商品图片通过Django文件系统管理

### 2.3 商品导出模块

商品导出模块允许用户选择商品并导出为WooCommerce兼容的CSV格式。

**主要功能**：
- 导出清单管理
- 导出选项配置
- CSV生成下载

**技术实现**：
- 前端使用Vuex/Pinia管理选中的商品
- 后端使用pandas处理CSV生成
- 符合WooCommerce CSV导入规范

### 2.4 商品展示模块

商品展示模块提供商品浏览、搜索和过滤功能。

**主要功能**：
- 商品列表展示
- 商品搜索
- 商品过滤
- 商品排序
- 分页浏览

**技术实现**：
- Vue组件构建响应式UI
- Element Plus提供UI组件
- 前端排序和过滤结合后端API查询
- 懒加载优化性能

## 3. 数据设计概述

### 3.1 核心实体

系统主要包含以下核心实体：

- **用户(User)**：系统用户信息
- **角色(Role)**：用户角色（Admin/Member）
- **商品(Product)**：基本商品信息
- **商品变体(ProductVariation)**：商品的变体信息
- **商品分类(Category)**：商品分类层级
- **商品属性(Attribute)**：商品的属性定义
- **属性值(AttributeValue)**：属性的可选值
- **导出清单(ExportList)**：用户的导出清单
- **导出清单项(ExportListItem)**：导出清单中的商品

### 3.2 数据关系概述

![实体关系图](https://placeholder-for-erd-diagram.com)

- 一个用户可以有多个导出清单
- 一个导出清单包含多个导出清单项
- 一个商品可以有多个商品变体
- 一个商品可以属于多个分类
- 商品变体通过属性和属性值组合定义

## 4. 接口设计概述

系统API遵循RESTful设计原则，使用JWT进行认证。

### 4.1 核心API端点

- **/api/auth/**：认证相关API
- **/api/users/**：用户管理API
- **/api/products/**：商品管理API
- **/api/categories/**：分类管理API
- **/api/attributes/**：属性管理API
- **/api/export-lists/**：导出清单管理API
- **/api/exports/**：导出功能API

### 4.2 API响应格式

所有API返回JSON格式，遵循以下基本结构：

```json
{
  "status": "success|error",
  "data": { ... },
  "message": "操作成功|错误消息",
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100
  }
}
```

## 5. 用户界面设计概述

系统采用扁平化设计风格，基于Element Plus组件库构建。

### 5.1 核心页面

- **登录/注册页**
- **仪表盘/首页**
- **商品列表页**
- **商品详情页**
- **商品编辑页**
- **导出清单管理页**
- **用户管理页（仅Admin）**

### 5.2 线框图

[简单线框图将在详细的系统设计文档中提供]

## 6. 安全设计

### 6.1 认证与授权

- 基于JWT的无状态认证
- 基于角色的权限控制
- API访问权限控制
- Token过期和刷新机制

### 6.2 数据安全

- 密码加密存储
- HTTPS传输加密
- 防SQL注入（使用ORM和参数化查询）
- CSRF防护
- XSS防护

## 7. 多语言支持

系统支持多语言，使用以下技术实现：

- 后端使用Django的国际化(i18n)功能
- 前端使用vue-i18n库
- 支持语言选择和切换
- 静态文本和动态内容均支持多语言

## 8. 部署架构

系统将部署在cPanel环境：

- **Web服务器**：Nginx
- **应用服务器**：Gunicorn
- **数据库服务器**：MySQL
- **静态资源**：通过Nginx直接提供
- **前端**：构建后部署为静态资源


