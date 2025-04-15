import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from .tenant_factories import TenantFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')
    nick_name = factory.Faker('name')
    # 电话号码限制为20个字符，使用固定格式生成
    phone = factory.Sequence(lambda n: f'1380013{n:04d}')
    tenant = factory.SubFactory(TenantFactory)
    is_member = True
    is_admin = False
    is_super_admin = False
    is_active = True


class TenantAdminFactory(UserFactory):
    is_member = True
    is_admin = True
    is_super_admin = False
    username = factory.Sequence(lambda n: f'tenant_admin{n}')


class SuperAdminFactory(UserFactory):
    is_member = True
    is_admin = True
    is_super_admin = True
    username = factory.Sequence(lambda n: f'super_admin{n}')
    # Super admin might not belong to a specific tenant
    tenant = None
