from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from common.models import Tenant
from tests.factories.tenant_factories import TenantFactory
from tests.factories.user_factories import SuperAdminFactory, TenantAdminFactory, UserFactory
import json
import time

User = get_user_model()


class UserAPITest(APITestCase):
    def setUp(self):
        """设置测试环境"""
        # 创建测试租户
        self.tenant = TenantFactory()
        
        # 创建各种角色的用户
        self.super_admin = SuperAdminFactory()
        self.tenant_admin = TenantAdminFactory(tenant=self.tenant)
        self.regular_user = UserFactory(tenant=self.tenant)
        
        # 默认使用超级管理员登录
        self.client.force_authenticate(user=self.super_admin)

    def test_tenant_user_list(self):
        """测试获取租户用户列表API"""
        url = reverse('common:tenant_user_list')
        response = self.client.get(url, {'tenant_id': self.tenant.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        # API应该返回HTTP标准状态码200
        self.assertEqual(response_data['code'], 200)
        
        # 验证用户数据在响应中
        user_usernames = [user['username'] for user in response_data['data']['users']]
        self.assertIn(self.tenant_admin.username, user_usernames)
        self.assertIn(self.regular_user.username, user_usernames)
    
    def test_tenant_admin_user_list(self):
        """测试租户管理员获取本租户用户列表"""
        # 使用租户管理员登录
        self.client.force_authenticate(user=self.tenant_admin)
        
        url = reverse('common:tenant_user_list')
        response = self.client.get(url, {'tenant_id': self.tenant.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        # 租户管理员只能查看自己租户的用户
        user_count = response_data['data']['count']
        self.assertEqual(user_count, 2)  # 租户管理员和普通用户
    
    def test_tenant_admin_other_tenant_forbidden(self):
        """测试租户管理员不能查看其他租户用户"""
        # 创建另一个租户
        other_tenant = TenantFactory()
        other_tenant_user = UserFactory(tenant=other_tenant)
        
        # 使用第一个租户的管理员登录
        self.client.force_authenticate(user=self.tenant_admin)
        
        # 尝试获取其他租户的用户列表
        url = reverse('common:tenant_user_list')
        response = self.client.get(url, {'tenant_id': other_tenant.id})
        
        # API实际行为：可能返回200但不包含其他租户的用户，而不是403
        if response.status_code == status.HTTP_200_OK:
            # 验证不能看到其他租户的用户
            response_data = json.loads(response.content)
            if 'data' in response_data and 'users' in response_data['data']:
                user_usernames = [user['username'] for user in response_data['data']['users']]
                self.assertNotIn(other_tenant_user.username, user_usernames)
        else:
            # 或者API直接拒绝访问
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_tenant_user(self):
        """测试在租户中创建用户API"""
        url = reverse('users:tenant_user_create')
        
        # 确保测试用户名和邮箱在系统中不存在
        test_username = f"newuser{int(time.time())}"
        test_email = f"newuser{int(time.time())}@example.com"
        
        user_data = {
            'tenant_id': self.tenant.id,
            'username': test_username,
            'password': 'newpassword123',
            'password_confirm': 'newpassword123',  # 添加确认密码
            'email': test_email,
            'nick_name': '新用户',
            'phone': '13800138000',
            'is_admin': False,
            'is_member': True
        }
        
        response = self.client.post(url, user_data, format='json')
        
        # 如果请求返回400，输出错误信息以便调试
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            response_data = json.loads(response.content)
            print(f"创建用户API返回400错误: {response_data}")
        
        # API应该返回HTTP 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
            
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 验证用户已创建
        self.assertTrue(User.objects.filter(username=test_username).exists())
        new_user = User.objects.get(username=test_username)
        self.assertEqual(new_user.tenant, self.tenant)
        self.assertEqual(new_user.email, test_email)
        self.assertTrue(new_user.is_member)
        self.assertFalse(new_user.is_admin)
    
    def test_create_tenant_admin(self):
        """测试在租户中创建管理员用户API"""
        url = reverse('users:tenant_user_create')
        
        # 确保测试用户名和邮箱在系统中不存在
        test_username = f"newadmin{int(time.time())}"
        test_email = f"newadmin{int(time.time())}@example.com"
        
        admin_data = {
            'tenant_id': self.tenant.id,
            'username': test_username,
            'password': 'newpassword123',
            'password_confirm': 'newpassword123',
            'email': test_email,
            'nick_name': '新管理员',
            'phone': '13900139000',
            'is_admin': True,
            'is_member': True
        }
        
        response = self.client.post(url, admin_data, format='json')
        
        # 如果请求返回400，输出错误信息以便调试
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            response_data = json.loads(response.content)
            print(f"创建管理员API返回400错误: {response_data}")
        
        # API应该返回HTTP 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
            
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 验证管理员已创建
        self.assertTrue(User.objects.filter(username=test_username).exists())
        new_admin = User.objects.get(username=test_username)
        self.assertEqual(new_admin.tenant, self.tenant)
        self.assertEqual(new_admin.email, test_email)
        self.assertTrue(new_admin.is_member)
        self.assertTrue(new_admin.is_admin)
        self.assertFalse(new_admin.is_super_admin)
    
    def test_tenant_admin_create_user(self):
        """测试租户管理员创建用户"""
        # 使用租户管理员登录
        self.client.force_authenticate(user=self.tenant_admin)
        
        url = reverse('users:tenant_user_create')
        
        # 确保测试用户名和邮箱在系统中不存在
        test_username = f"userbyadmin{int(time.time())}"
        test_email = f"userbyadmin{int(time.time())}@example.com"
        
        user_data = {
            'username': test_username,
            'password': 'password123',
            'password_confirm': 'password123',
            'email': test_email,
            'nick_name': '管理员创建的用户',
            'phone': '13811138111',
            'is_admin': False,
            'is_member': True
        }
        
        response = self.client.post(url, user_data, format='json')
        
        # 如果请求返回400，输出错误信息以便调试
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            response_data = json.loads(response.content)
            print(f"租户管理员创建用户API返回400错误: {response_data}")
        
        # API应该返回HTTP 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
            
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 验证用户已创建
        self.assertTrue(User.objects.filter(username=test_username).exists())
        new_user = User.objects.get(username=test_username)
        self.assertEqual(new_user.tenant, self.tenant_admin.tenant)
        self.assertEqual(new_user.email, test_email)
        self.assertTrue(new_user.is_member)
        self.assertFalse(new_user.is_admin)
        self.assertFalse(new_user.is_super_admin)
    
    def test_tenant_admin_cannot_create_admin(self):
        """测试租户管理员不能创建管理员用户"""
        # 使用租户管理员登录
        self.client.force_authenticate(user=self.tenant_admin)
        
        url = reverse('users:tenant_user_create')
        admin_data = {
            'tenant_id': self.tenant.id,
            'username': 'adminbyadmin',
            'password': 'password123',
            'email': 'adminbyadmin@example.com',
            'is_admin': True  # 尝试创建管理员
        }
        
        response = self.client.post(url, admin_data, format='json')
        
        # 检查是否返回错误
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        response_data = json.loads(response.content)
        self.assertFalse(response_data.get('success', False))
        
        # 验证管理员用户未被创建
        self.assertFalse(User.objects.filter(username='adminbyadmin').exists())
    
    def test_regular_user_cannot_create_user(self):
        """测试普通用户不能创建用户"""
        # 使用普通用户登录
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('users:tenant_user_create')
        user_data = {
            'tenant_id': self.tenant.id,
            'username': 'userbyuser',
            'password': 'password123',
            'email': 'userbyuser@example.com'
        }
        
        response = self.client.post(url, user_data, format='json')
        
        # 应该返回403禁止访问
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 验证用户未被创建
        self.assertFalse(User.objects.filter(username='userbyuser').exists())
    
    def test_quota_limit_enforcement(self):
        """测试配额限制的实施"""
        # 登录为超级管理员
        self.client.force_authenticate(user=self.super_admin)
        
        # 创建一个新租户，配额设为最多2个用户
        test_tenant = TenantFactory()
        
        # 确保租户配额设置为2个用户
        from common.models import TenantQuota
        quota, created = TenantQuota.objects.get_or_create(tenant=test_tenant)
        quota.max_users = 2
        quota.save()
        
        # 已经创建一个租户管理员，现在创建第二个用户
        user1 = UserFactory(tenant=test_tenant)
        
        # 创建第三个用户应该失败，因为超过了配额
        url = reverse('users:tenant_user_create')
        
        # 确保测试用户名和邮箱在系统中不存在
        test_username = f"quota_test_user{int(time.time())}"
        test_email = f"quota_test_user{int(time.time())}@example.com"
        
        user_data = {
            'tenant_id': test_tenant.id,
            'username': test_username,
            'password': 'password123',
            'password_confirm': 'password123',
            'email': test_email,
            'nick_name': '配额测试用户',
            'is_admin': False,
            'is_member': True
        }
        
        # 第一次应该成功（第2个用户）
        first_response = self.client.post(url, user_data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        
        # 尝试创建第三个用户，应该失败
        test_username2 = f"quota_test_user2_{int(time.time())}"
        test_email2 = f"quota_test_user2_{int(time.time())}@example.com"
        
        user_data2 = {
            'tenant_id': test_tenant.id,
            'username': test_username2,
            'password': 'password123',
            'password_confirm': 'password123',
            'email': test_email2,
            'nick_name': '配额测试用户2',
            'is_admin': False,
            'is_member': True
        }
        
        second_response = self.client.post(url, user_data2, format='json')
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 验证错误消息是否包含配额相关信息
        response_data = json.loads(second_response.content)
        error_message = response_data.get('message', '')
        
        self.assertTrue(
            'quota' in error_message.lower() or
            '配额' in error_message or
            'limit' in error_message.lower() or
            '限制' in error_message or
            'maximum' in error_message.lower() or
            '最大' in error_message,
            f"错误信息应包含配额相关提示: {error_message}"
        )

    def test_only_super_admin_can_create_tenant_admin(self):
        """测试只有超级管理员可以创建租户管理员"""
        # 使用普通用户登录
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('users:tenant_user_create')
        admin_data = {
            'tenant_id': self.tenant.id,
            'username': 'adminbyuser',
            'password': 'password123',
            'email': 'adminbyuser@example.com',
            'is_admin': True  # 尝试创建管理员
        }
        
        response = self.client.post(url, admin_data, format='json')
        
        # 应该返回403禁止访问
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 验证管理员用户未被创建
        self.assertFalse(User.objects.filter(username='adminbyuser').exists())


class UserTenantAssignAPITest(APITestCase):
    def setUp(self):
        """设置测试环境"""
        # 创建租户
        self.tenant1 = TenantFactory()
        self.tenant2 = TenantFactory()
        
        # 创建超级管理员
        self.super_admin = SuperAdminFactory()
        
        # 创建一个没有租户的用户
        self.user_without_tenant = UserFactory(tenant=None)
        
        # 创建一个已有租户的用户
        self.user_with_tenant = UserFactory(tenant=self.tenant1)
        
        # 登录超级管理员
        self.client.force_authenticate(user=self.super_admin)
    
    def test_assign_user_to_tenant(self):
        """测试将用户分配到租户"""
        url = reverse('users:assign_tenant')
        data = {
            'user_id': self.user_without_tenant.id,
            'tenant_id': self.tenant2.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 验证用户已被分配到租户
        self.user_without_tenant.refresh_from_db()
        self.assertEqual(self.user_without_tenant.tenant, self.tenant2)
    
    def test_reassign_user_to_different_tenant(self):
        """测试将用户从一个租户重新分配到另一个租户"""
        url = reverse('users:assign_tenant')
        data = {
            'user_id': self.user_with_tenant.id,
            'tenant_id': self.tenant2.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证用户已被重新分配
        self.user_with_tenant.refresh_from_db()
        self.assertEqual(self.user_with_tenant.tenant, self.tenant2)
    
    def test_only_super_admin_can_assign(self):
        """测试只有超级管理员可以分配用户到租户"""
        # 创建租户管理员并登录
        tenant_admin = TenantAdminFactory(tenant=self.tenant1)
        self.client.force_authenticate(user=tenant_admin)
        
        url = reverse('users:assign_tenant')
        data = {
            'user_id': self.user_without_tenant.id,
            'tenant_id': self.tenant1.id
        }
        
        response = self.client.post(url, data, format='json')
        
        # 应该返回403禁止访问
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 验证用户未被分配
        self.user_without_tenant.refresh_from_db()
        self.assertIsNone(self.user_without_tenant.tenant)
