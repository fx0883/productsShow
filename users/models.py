from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """
    扩展Django内置用户模型
    """
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    is_admin = models.BooleanField(default=False)
    is_member = models.BooleanField(default=True)
    
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
