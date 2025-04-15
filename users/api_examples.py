"""
用户API示例模块 - 包含API文档示例数据
"""
from drf_yasg.openapi import (
    Schema, 
    TYPE_OBJECT, 
    TYPE_STRING, 
    TYPE_INTEGER, 
    TYPE_BOOLEAN, 
    TYPE_ARRAY,
    Items,
    Parameter,
    IN_QUERY
)
from drf_yasg.utils import swagger_auto_schema

# 注册API示例
register_request_example = {
    'username': 'testuser',
    'email': 'test@example.com',
    'phone': '13800138000',
    'password': 'Secure@Password123',
    'password_confirm': 'Secure@Password123',
    'nick_name': '测试用户'
}

register_response_example = {
    'success': True,
    'code': 201,
    'message': '注册成功',
    'data': {
        'user': {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '13800138000',
            'is_admin': False,
            'is_member': True,
            'date_joined': '2025-04-12T13:25:30Z',
            'last_login': None,
            'nick_name': '测试用户',
            'avatar': None
        },
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.abcdefghijklmnopqrstuvwxyz',
        'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.123456789abcdefghijklmnopqrst',
        'token_type': 'Bearer'
    }
}

register_400_example = {
    'success': False,
    'code': 400,
    'message': '注册失败，请检查输入',
    'data': {
        'username': ['该用户名已存在'],
        'email': ['该邮箱已被注册'],
        'password': ['密码过于简单，请使用包含字母、数字和特殊字符的组合']
    }
}

# 登录API示例
login_request_example = {
    'username': 'testuser',
    'password': 'Secure@Password123'
}

login_with_email_example = {
    'email': 'test@example.com',
    'password': 'Secure@Password123'
}

login_response_example = {
    'success': True,
    'code': 200,
    'message': '登录成功',
    'data': {
        'user': {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '13800138000',
            'is_admin': False,
            'is_member': True,
            'date_joined': '2025-04-12T13:25:30Z',
            'last_login': '2025-04-12T13:30:45Z',
            'nick_name': '测试用户',
            'avatar': 'http://localhost:8000/media/avatars/user1.jpg'
        },
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.abcdefghijklmnopqrstuvwxyz',
        'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.123456789abcdefghijklmnopqrst',
        'token_type': 'Bearer'
    }
}

login_400_example = {
    'success': False,
    'code': 400,
    'message': '登录失败，请检查用户名和密码',
    'data': {
        'non_field_errors': ['用户名或密码错误']
    }
}

# 登出API示例
logout_response_example = {
    'success': True,
    'code': 200,
    'message': '登出成功',
    'data': None
}

# 刷新令牌API示例
refresh_token_request_example = {
    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.123456789abcdefghijklmnopqrst'
}

refresh_token_response_example = {
    'success': True,
    'code': 200,
    'message': '令牌刷新成功',
    'data': {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.new_access_token_xyz',
        'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.new_refresh_token_123',
        'token_type': 'Bearer'
    }
}

refresh_token_400_example = {
    'success': False,
    'code': 400,
    'message': '令牌刷新失败',
    'data': {
        'refresh_token': ['无效的刷新令牌']
    }
}

# 用户资料API示例
user_profile_response_example = {
    'success': True,
    'code': 200,
    'message': '获取用户资料成功',
    'data': {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
        'phone': '13800138000',
        'is_admin': False,
        'is_member': True,
        'date_joined': '2025-04-12T13:25:30Z',
        'last_login': '2025-04-12T13:30:45Z',
        'profile': {
            'preferred_language': 'zh-cn',
            'date_format': 'YYYY-MM-DD'
        },
        'first_name': '张',
        'last_name': '三',
        'nick_name': '张三丰',
        'avatar': 'http://localhost:8000/media/avatars/user1.jpg'
    }
}

user_profile_update_request_example = {
    'username': 'newusername',
    'phone': '13900139000',
    'first_name': '李',
    'last_name': '四',
    'nick_name': '李四方',
    'profile': {
        'preferred_language': 'en-us',
        'date_format': 'MM/DD/YYYY'
    }
}

user_profile_update_response_example = {
    'success': True,
    'code': 200,
    'message': '更新用户资料成功',
    'data': {
        'id': 1,
        'username': 'newusername',
        'email': 'test@example.com',
        'phone': '13900139000',
        'is_admin': False,
        'is_member': True,
        'date_joined': '2025-04-12T13:25:30Z',
        'last_login': '2025-04-12T13:30:45Z',
        'profile': {
            'preferred_language': 'en-us',
            'date_format': 'MM/DD/YYYY'
        },
        'first_name': '李',
        'last_name': '四',
        'nick_name': '李四方',
        'avatar': 'http://localhost:8000/media/avatars/user1.jpg'
    }
}

user_profile_update_400_example = {
    'success': False,
    'code': 400,
    'message': '更新用户资料失败',
    'data': {
        'username': ['该用户名已被占用'],
        'phone': ['手机号格式不正确']
    }
}

# 修改密码API示例
change_password_request_example = {
    'old_password': 'Secure@Password123',
    'new_password': 'NewSecure@Password456',
    'confirm_password': 'NewSecure@Password456'
}

change_password_response_example = {
    'success': True,
    'code': 200,
    'message': '密码修改成功',
    'data': {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.abcdefghijklmnopqrstuvwxyz',
        'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTYxMjM1MzAsImlhdCI6MTcxNjEyMzUzMH0.123456789abcdefghijklmnopqrst',
        'token_type': 'Bearer'
    }
}

change_password_400_example = {
    'success': False,
    'code': 400,
    'message': '密码修改失败',
    'data': {
        'old_password': ['密码不正确'],
        'new_password': ['新密码不能与旧密码相同'],
        'confirm_password': ['两次密码不一致']
    }
}

# 用户管理API示例（管理员）
user_list_response_example = {
    'success': True,
    'code': 200,
    'message': '获取用户列表成功',
    'data': [
        {
            'id': 1,
            'username': 'admin',
            'email': 'admin@example.com',
            'phone': '13800138000',
            'is_admin': True,
            'is_member': False,
            'date_joined': '2025-04-10T10:00:00Z',
            'last_login': '2025-04-12T13:00:00Z',
            'nick_name': '系统管理员',
            'avatar': 'http://localhost:8000/media/avatars/admin.jpg'
        },
        {
            'id': 2,
            'username': 'member1',
            'email': 'member1@example.com',
            'phone': '13900139000',
            'is_admin': False,
            'is_member': True,
            'date_joined': '2025-04-11T11:00:00Z',
            'last_login': '2025-04-12T12:00:00Z',
            'nick_name': '普通会员',
            'avatar': 'http://localhost:8000/media/avatars/member1.jpg'
        }
    ],
    'pagination': {
        'page': 1,
        'per_page': 10,
        'total_pages': 1,
        'total_items': 2
    }
}

create_user_request_example = {
    'username': 'newadmin',
    'email': 'newadmin@example.com',
    'phone': '13700137000',
    'password': 'Secure@Password123',
    'password_confirm': 'Secure@Password123',
    'is_admin': True,
    'is_member': False,
    'nick_name': '新管理员'
}

create_user_response_example = {
    'success': True,
    'code': 201,
    'message': '创建用户成功',
    'data': {
        'id': 3,
        'username': 'newadmin',
        'email': 'newadmin@example.com',
        'phone': '13700137000',
        'is_admin': True,
        'is_member': False,
        'date_joined': '2025-04-12T13:45:00Z',
        'last_login': None,
        'nick_name': '新管理员',
        'avatar': None
    }
}

create_user_400_example = {
    'success': False,
    'code': 400,
    'message': '创建用户失败',
    'data': {
        'username': ['该用户名已存在'],
        'email': ['该邮箱已被注册'],
        'password': ['密码过于简单']
    }
}

# 用户详情API示例（管理员）
user_detail_response_example = {
    'success': True,
    'code': 200,
    'message': '获取用户详情成功',
    'data': {
        'id': 2,
        'username': 'member1',
        'email': 'member1@example.com',
        'phone': '13900139000',
        'is_admin': False,
        'is_member': True,
        'date_joined': '2025-04-11T11:00:00Z',
        'last_login': '2025-04-12T12:00:00Z',
        'profile': {
            'preferred_language': 'zh-cn',
            'date_format': 'YYYY-MM-DD'
        },
        'first_name': '张',
        'last_name': '三',
        'nick_name': '张三丰',
        'avatar': 'http://localhost:8000/media/avatars/member1.jpg'
    }
}

user_detail_404_example = {
    'success': False,
    'code': 404,
    'message': '用户不存在',
    'data': None
}

update_user_request_example = {
    'username': 'updatedmember',
    'phone': '13600136000',
    'is_admin': False,
    'is_member': True,
    'first_name': '王',
    'last_name': '五',
    'nick_name': '王五爵',
    'profile': {
        'preferred_language': 'en-us',
        'date_format': 'MM/DD/YYYY'
    }
}

update_user_response_example = {
    'success': True,
    'code': 200,
    'message': '更新用户成功',
    'data': {
        'id': 2,
        'username': 'updatedmember',
        'email': 'member1@example.com',
        'phone': '13600136000',
        'is_admin': False,
        'is_member': True,
        'date_joined': '2025-04-11T11:00:00Z',
        'last_login': '2025-04-12T12:00:00Z',
        'profile': {
            'preferred_language': 'en-us',
            'date_format': 'MM/DD/YYYY'
        },
        'first_name': '王',
        'last_name': '五',
        'nick_name': '王五爵',
        'avatar': 'http://localhost:8000/media/avatars/member1.jpg'
    }
}

update_user_404_example = {
    'success': False,
    'code': 404,
    'message': '用户不存在',
    'data': None
}

update_user_400_example = {
    'success': False,
    'code': 400,
    'message': '更新用户失败',
    'data': {
        'username': ['该用户名已被占用']
    }
}

delete_user_response_example = {
    'success': True,
    'code': 200,
    'message': '删除用户成功',
    'data': None
}

delete_user_404_example = {
    'success': False,
    'code': 404,
    'message': '用户不存在',
    'data': None
}

# 密码重置API示例
reset_password_request_example = {
    'user_id': 2,
    'super_key': '123456'
}

reset_password_response_example = {
    'success': True,
    'code': 200,
    'message': '密码重置成功，新密码为: 123456',
    'data': {
        'user_id': 2,
        'username': 'member1'
    }
}

reset_password_400_example = {
    'success': False,
    'code': 400,
    'message': '超级密钥不正确',
    'data': None
}

reset_password_404_example = {
    'success': False,
    'code': 404,
    'message': '用户不存在',
    'data': None
}

# 重置密码错误响应示例
reset_password_404_example = {
    "success": False,
    "code": 404,
    "message": "用户不存在",
    "data": None
}

# 用户租户分配请求示例
user_tenant_assign_request_example = {
    "user_id": 2,
    "tenant_id": 3
}

# 用户租户分配成功响应示例
user_tenant_assign_response_example = {
    "success": True,
    "code": 200,
    "message": "用户租户分配成功",
    "data": {
        "user_id": 2,
        "username": "member1",
        "tenant_id": 3,
        "tenant_name": "测试租户"
    }
}

# 用户租户分配错误响应示例
user_tenant_assign_400_example = {
    "success": False,
    "code": 400,
    "message": "用户租户分配失败",
    "data": {
        "user_id": ["用户不存在"],
        "tenant_id": ["租户不存在"]
    }
}

# 租户用户创建请求示例
tenant_user_create_request_example = {
    "username": "tenant_user1",
    "email": "tenant_user1@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "phone": "13812345678",
    "nick_name": "租户用户1",
    "is_admin": False,
    "is_member": True
}

# 租户用户创建成功响应示例
tenant_user_create_response_example = {
    "success": True,
    "code": 201,
    "message": "用户创建成功",
    "data": {
        "user_id": 5,
        "username": "tenant_user1",
        "email": "tenant_user1@example.com",
        "is_admin": False,
        "is_member": True,
        "tenant_id": 2,
        "tenant_name": "测试租户"
    }
}

# 租户用户创建错误响应示例
tenant_user_create_400_example = {
    "success": False,
    "code": 400,
    "message": "用户创建失败",
    "data": {
        "username": ["该用户名已存在"],
        "email": ["该邮箱已被注册"],
        "password_confirm": ["两次密码输入不一致"]
    }
}
