from django.db import models
from users.models import User
from products.models import Product, ProductVariation

# Create your models here.

class ExportList(models.Model):
    """
    用户导出清单
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_lists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'export_lists'
        verbose_name = '导出清单'
        verbose_name_plural = '导出清单'
        
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class ExportListItem(models.Model):
    """
    导出清单项
    """
    export_list = models.ForeignKey(ExportList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'export_list_items'
        verbose_name = '导出清单项'
        verbose_name_plural = '导出清单项'
        constraints = [
            models.CheckConstraint(
                check=models.Q(product__isnull=False) | models.Q(variation__isnull=False),
                name="either_product_or_variation"
            )
        ]
        
    def __str__(self):
        if self.product:
            return f"产品: {self.product.name}"
        return f"变体: {self.variation.sku}"


class ExportTemplate(models.Model):
    """
    CSV导出模板
    """
    FORMAT_CHOICES = (
        ('woocommerce', 'WooCommerce'),
        ('custom', '自定义'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='woocommerce')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_templates')
    is_public = models.BooleanField(default=False)
    fields = models.JSONField(default=dict, help_text="要导出的字段配置")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'export_templates'
        verbose_name = '导出模板'
        verbose_name_plural = '导出模板'
        
    def __str__(self):
        return f"{self.name} ({self.format})"


class ExportHistory(models.Model):
    """
    导出历史记录
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_history')
    export_list = models.ForeignKey(ExportList, on_delete=models.CASCADE, null=True, blank=True)
    template = models.ForeignKey(ExportTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    product_count = models.IntegerField(default=0)
    variation_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'export_history'
        verbose_name = '导出历史'
        verbose_name_plural = '导出历史'
        
    def __str__(self):
        return f"{self.file_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
