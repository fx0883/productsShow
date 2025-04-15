"""
租户相关API示例
"""

# 租户列表请求示例
tenant_list_response_example = {
    "success": True,
    "code": 200,
    "message": "获取租户列表成功",
    "data": [
        {
            "id": 1,
            "name": "租户1",
            "status": "active",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "租户2",
            "status": "active",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    ]
}

# 租户创建请求示例
tenant_create_request_example = {
    "name": "新租户",
    "status": "active"
}

# 租户创建成功响应示例
tenant_create_response_example = {
    "success": True,
    "code": 201,
    "message": "租户创建成功",
    "data": {
        "name": "新租户",
        "status": "active"
    }
}

# 租户创建失败响应示例
tenant_create_400_example = {
    "success": False,
    "code": 400,
    "message": "租户创建失败",
    "data": {
        "name": ["租户名称已存在"]
    }
}

# 租户详情响应示例
tenant_detail_response_example = {
    "success": True,
    "code": 200,
    "message": "获取租户详情成功",
    "data": {
        "id": 1,
        "name": "租户1",
        "status": "active",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "user_count": 10,
        "admin_count": 2,
        "member_count": 8,
        "quota": {
            "id": 1,
            "tenant": 1,
            "tenant_name": "租户1",
            "max_users": 20,
            "max_admins": 5,
            "max_storage_mb": 1024,
            "max_products": 100,
            "current_storage_used_mb": 256,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        "storage_usage_percent": 25.0,
        "user_usage_percent": 50.0,
        "admin_usage_percent": 40.0,
        "product_usage_percent": 30.0
    }
}

# 租户更新请求示例
tenant_update_request_example = {
    "name": "租户1更新",
    "status": "active"
}

# 租户更新成功响应示例
tenant_update_response_example = {
    "success": True,
    "code": 200,
    "message": "租户更新成功",
    "data": {
        "id": 1,
        "name": "租户1更新",
        "status": "active",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}

# 租户更新失败响应示例
tenant_update_400_example = {
    "success": False,
    "code": 400,
    "message": "租户更新失败",
    "data": {
        "name": ["租户名称已存在"]
    }
}

# 租户删除成功响应示例
tenant_delete_response_example = {
    "success": True,
    "code": 204,
    "message": "租户删除成功",
    "data": None
}

# 租户不存在响应示例
tenant_not_found_example = {
    "success": False,
    "code": 404,
    "message": "租户不存在",
    "data": None
}

# 租户用户列表响应示例
tenant_user_list_response_example = {
    "success": True,
    "code": 200,
    "message": "获取租户用户列表成功",
    "data": {
        "tenant": {
            "id": 1,
            "name": "租户1",
            "status": "active"
        },
        "users": {
            "count": 10,
            "page": 1,
            "page_size": 10,
            "total_pages": 1,
            "results": [
                {
                    "id": 1,
                    "username": "user1",
                    "email": "user1@example.com",
                    "nick_name": "用户1",
                    "is_admin": False,
                    "is_member": True,
                    "is_super_admin": False,
                    "created_at": "2023-01-01T00:00:00Z"
                }
            ]
        }
    }
}

# 租户用户列表查询错误响应示例
tenant_user_list_400_example = {
    "success": False,
    "code": 400,
    "message": "超级管理员必须指定租户ID",
    "data": None
}

# 租户配额信息请求示例
tenant_quota_request_example = {
    "tenant": 1,
    "max_users": 20,
    "max_admins": 5,
    "max_storage_mb": 2048,
    "max_products": 200
}

# 租户配额信息响应示例
tenant_quota_response_example = {
    "success": True,
    "code": 200,
    "message": "获取租户配额成功",
    "data": {
        "id": 1,
        "tenant": 1,
        "tenant_name": "租户1",
        "max_users": 10,
        "max_admins": 2,
        "max_storage_mb": 1024,
        "max_products": 100,
        "current_storage_used_mb": 50,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}

# 租户配额更新成功响应示例
tenant_quota_update_response_example = {
    "success": True,
    "code": 200,
    "message": "更新租户配额成功",
    "data": {
        "id": 1,
        "tenant": 1,
        "tenant_name": "租户1",
        "max_users": 20,
        "max_admins": 5,
        "max_storage_mb": 2048,
        "max_products": 200,
        "current_storage_used_mb": 50,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
}

# 租户配额更新失败响应示例
tenant_quota_update_400_example = {
    "success": False,
    "code": 400,
    "message": "参数错误",
    "data": {
        "max_users": ["此字段是必须的。"],
        "max_storage_mb": ["此字段是必须的。"]
    }
}
