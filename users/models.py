from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from common.models import Tenant  # 导入Tenant模型

# Create your models here.

class User(AbstractUser):
    """
    扩展Django内置用户模型
    """
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    is_admin = models.BooleanField(default=False)
    is_member = models.BooleanField(default=True)
    # 添加租户字段，默认为NULL，但会通过迁移脚本为现有用户设置为租户ID 1
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='users',
        verbose_name='租户',
        null=True,  # 允许为空，便于迁移现有数据
        db_index=True
    )
    # 新增超级管理员标志，用于标识可以管理所有租户的超级管理员
    is_super_admin = models.BooleanField(default=False, verbose_name='超级管理员')
    nick_name = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$',
                message='昵称只能包含字母、数字、下划线和中文',
                code='invalid_nickname'
            )
        ]
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'


class UserProfile(models.Model):
    """
    用户额外信息
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_language = models.CharField(max_length=10, default='zh-cn')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'


class UserToken(models.Model):
    """
    用户JWT令牌管理
    """
    TOKEN_TYPE_CHOICES = (
        ('access', '访问令牌'),
        ('refresh', '刷新令牌'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES, default='access')
    is_valid = models.BooleanField(default=True)
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_tokens'
        verbose_name = '用户令牌'
        verbose_name_plural = '用户令牌'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'token_type']),
        ]
    
    @property
    def is_expired(self):
        """检查令牌是否已过期"""
        from django.utils import timezone
        return not self.is_valid or self.expired_at < timezone.now()
