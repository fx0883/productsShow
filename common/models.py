from django.db import models
from django.utils.translation import gettext_lazy as _
from .tenant_middleware import get_current_tenant


class TenantManager(models.Manager):
    """
    租户模型管理器
    自动根据当前租户过滤查询集
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


# Create your models here.

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
    is_deleted = models.BooleanField(_("是否删除"), default=False)
    
    class Meta:
        db_table = 'tenants'
        verbose_name = _('租户')
        verbose_name_plural = _('租户')
        ordering = ['id']
    
    def __str__(self):
        return self.name


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
    
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True, null=True)
    
    class Meta:
        db_table = 'tenant_quotas'
        verbose_name = _('租户配额')
        verbose_name_plural = _('租户配额')
    
    def __str__(self):
        return f"{self.tenant.name}的配额"
    
    def is_user_quota_exceeded(self):
        """检查是否超过用户配额"""
        from users.models import User
        current_users = User.objects.filter(tenant=self.tenant).count()
        return current_users >= self.max_users
    
    def is_admin_quota_exceeded(self):
        """检查是否超过管理员配额"""
        from users.models import User
        current_admins = User.objects.filter(tenant=self.tenant, is_admin=True).count()
        return current_admins >= self.max_admins
    
    def is_storage_quota_exceeded(self, additional_mb=0):
        """检查是否超过存储配额"""
        return (self.current_storage_used_mb + additional_mb) > self.max_storage_mb
    
    def is_product_quota_exceeded(self):
        """检查是否超过产品配额"""
        from products.models import Product
        current_products = Product.objects.filter(tenant=self.tenant).count()
        return current_products >= self.max_products
    
    def update_storage_usage(self):
        """更新存储使用情况"""
        # 计算所有产品图片大小
        from products.models import ProductImage
        from django.db.models import Sum
        
        # 获取所有图片文件大小总和，单位转换为MB
        product_images = ProductImage.objects.filter(tenant=self.tenant)
        total_size = 0
        
        for img in product_images:
            if img.image and hasattr(img.image, 'size'):
                total_size += img.image.size
        
        # 换算为MB并保存
        self.current_storage_used_mb = total_size / (1024 * 1024)
        self.save(update_fields=['current_storage_used_mb', 'updated_at'])


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
        null=True  # 允许为空，便于迁移现有数据
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
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        """
        重写保存方法，自动设置租户
        如果没有指定租户，则使用当前线程的租户
        """
        if not self.tenant:
            # 如果没有指定租户，则使用当前线程的租户
            self.tenant = get_current_tenant()
        super().save(*args, **kwargs)
