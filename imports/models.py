from django.db import models
from users.models import User

# Create your models here.

class ImportHistory(models.Model):
    """
    导入历史记录
    """
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    )
    
    FORMAT_CHOICES = (
        ('woocommerce', 'WooCommerce'),
        ('custom', '自定义'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_history')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='woocommerce')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    success_rows = models.IntegerField(default=0)
    error_rows = models.IntegerField(default=0)
    product_count = models.IntegerField(default=0)
    variation_count = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'import_history'
        verbose_name = '导入历史'
        verbose_name_plural = '导入历史'
        
    def __str__(self):
        return f"{self.file_name} ({self.status})"


class ImportMapping(models.Model):
    """
    CSV导入字段映射
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_mappings')
    is_public = models.BooleanField(default=False)
    source_format = models.CharField(max_length=50, default='woocommerce')
    field_mapping = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'import_mappings'
        verbose_name = '导入映射'
        verbose_name_plural = '导入映射'
        
    def __str__(self):
        return f"{self.name} ({self.source_format})"
