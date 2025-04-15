import factory
from factory.django import DjangoModelFactory
from common.models import Tenant, TenantQuota


class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant

    name = factory.Sequence(lambda n: f"测试租户{n}")
    status = "active"

    @factory.post_generation
    def create_quota(self, create, extracted, **kwargs):
        """创建后自动创建配额"""
        if not create:
            return
            
        # 创建租户配额
        TenantQuota.objects.create(
            tenant=self,
            max_users=10,
            max_admins=2,
            max_storage_mb=1024,
            max_products=100,
            current_storage_used_mb=0
        )


class TenantQuotaFactory(DjangoModelFactory):
    class Meta:
        model = TenantQuota

    tenant = factory.SubFactory(TenantFactory)
    max_users = 10
    max_admins = 2
    max_storage_mb = 1024
    max_products = 100
    current_storage_used_mb = 0
