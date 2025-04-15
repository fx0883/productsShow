from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from common.models import Tenant, BaseModel
from common.tenant_middleware import set_current_tenant, get_current_tenant
from common.tenant_middleware import TenantMiddleware
from tests.factories.tenant_factories import TenantFactory
from tests.factories.user_factories import UserFactory, TenantAdminFactory, SuperAdminFactory
from django.db import models
from django.db.models.query import QuerySet

User = get_user_model()


# 创建一个测试模型，继承自BaseModel
class TestTenantModel(BaseModel):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'common'  # 使用已存在的应用标签以避免注册新应用
        abstract = True  # 标记为抽象模型，不会创建数据库表


class TenantIsolationTest(TestCase):
    def setUp(self):
        """设置测试环境"""
        # 创建测试租户
        self.tenant1 = TenantFactory(name="租户1")
        self.tenant2 = TenantFactory(name="租户2")
        
        # 创建各租户的用户
        self.user1 = UserFactory(tenant=self.tenant1)
        self.user2 = UserFactory(tenant=self.tenant2)
        self.admin1 = TenantAdminFactory(tenant=self.tenant1)
        self.admin2 = TenantAdminFactory(tenant=self.tenant2)
        self.super_admin = SuperAdminFactory()
        
        # 请求工厂
        self.factory = RequestFactory()
        
        # 测试用的BaseModel实例
        # 注意：这里我们将使用现有的数据模型进行测试，而不是抽象的TestTenantModel
    
    def test_tenant_context_switching(self):
        """测试租户上下文切换"""
        # 初始情况下没有当前租户
        self.assertIsNone(get_current_tenant())
        
        # 设置当前租户为租户1
        set_current_tenant(self.tenant1)
        self.assertEqual(get_current_tenant(), self.tenant1)
        
        # 切换到租户2
        set_current_tenant(self.tenant2)
        self.assertEqual(get_current_tenant(), self.tenant2)
        
        # 清除租户上下文
        set_current_tenant(None)
        self.assertIsNone(get_current_tenant())
    
    def test_user_data_isolation(self):
        """测试用户数据隔离"""
        # 设置租户1上下文
        set_current_tenant(self.tenant1)
        
        # 获取租户1的用户
        users_in_tenant1 = User.objects.all()
        usernames_in_tenant1 = [user.username for user in users_in_tenant1]
        
        # 验证只能看到租户1的用户
        self.assertIn(self.user1.username, usernames_in_tenant1)
        self.assertIn(self.admin1.username, usernames_in_tenant1)
        self.assertNotIn(self.user2.username, usernames_in_tenant1)
        self.assertNotIn(self.admin2.username, usernames_in_tenant1)
        
        # 设置租户2上下文
        set_current_tenant(self.tenant2)
        
        # 获取租户2的用户
        users_in_tenant2 = User.objects.all()
        usernames_in_tenant2 = [user.username for user in users_in_tenant2]
        
        # 验证只能看到租户2的用户
        self.assertIn(self.user2.username, usernames_in_tenant2)
        self.assertIn(self.admin2.username, usernames_in_tenant2)
        self.assertNotIn(self.user1.username, usernames_in_tenant2)
        self.assertNotIn(self.admin1.username, usernames_in_tenant2)
    
    def test_super_admin_access(self):
        """测试超级管理员可以访问所有租户数据"""
        # 清除租户上下文
        set_current_tenant(None)
        
        # 使用original_objects可以看到所有租户的数据
        all_users = User.objects.all()
        
        # 验证可以看到所有用户
        usernames = [user.username for user in all_users]
        self.assertIn(self.user1.username, usernames)
        self.assertIn(self.admin1.username, usernames)
        self.assertIn(self.user2.username, usernames)
        self.assertIn(self.admin2.username, usernames)
        self.assertIn(self.super_admin.username, usernames)
    
    def test_tenant_middleware(self):
        """测试租户中间件设置租户上下文"""
        # 创建中间件实例
        middleware = TenantMiddleware(get_response=lambda req: None)
        
        # 测试租户1用户的请求
        request = self.factory.get('/')
        request.user = self.user1
        middleware.process_request(request)
        
        # 验证租户上下文被正确设置
        self.assertEqual(get_current_tenant(), self.tenant1)
        
        # 测试租户2用户的请求
        request = self.factory.get('/')
        request.user = self.user2
        middleware.process_request(request)
        
        # 验证租户上下文被正确切换
        self.assertEqual(get_current_tenant(), self.tenant2)
        
        # 测试超级管理员的请求
        request = self.factory.get('/')
        request.user = self.super_admin
        middleware.process_request(request)
        
        # 验证超级管理员不设置租户上下文
        self.assertIsNone(get_current_tenant())
    
    def test_tenant_admin_permissions(self):
        """测试租户管理员的权限范围"""
        # 设置租户1上下文
        set_current_tenant(self.tenant1)
        
        # 创建一个测试用户
        test_user = UserFactory(tenant=self.tenant1, username="test_user_in_tenant1")
        
        # 租户1管理员应该能看到租户1内的所有用户
        users_seen_by_admin1 = User.objects.all()
        usernames = [user.username for user in users_seen_by_admin1]
        self.assertIn(test_user.username, usernames)
        self.assertIn(self.user1.username, usernames)
        
        # 设置租户2上下文
        set_current_tenant(self.tenant2)
        
        # 创建一个测试用户
        test_user2 = UserFactory(tenant=self.tenant2, username="test_user_in_tenant2")
        
        # 租户2管理员应该能看到租户2内的所有用户，但看不到租户1的用户
        users_seen_by_admin2 = User.objects.all()
        usernames = [user.username for user in users_seen_by_admin2]
        self.assertIn(test_user2.username, usernames)
        self.assertIn(self.user2.username, usernames)
        self.assertNotIn(test_user.username, usernames)
        self.assertNotIn(self.user1.username, usernames)
