from django.contrib import admin
from .models import Tenant, TenantQuota

class TenantQuotaInline(admin.StackedInline):
    model = TenantQuota
    can_delete = False
    readonly_fields = ('current_storage_used_mb', 'created_at', 'updated_at', 
                      'get_user_quota_status', 'get_admin_quota_status', 
                      'get_product_quota_status', 'get_storage_quota_status')
    fieldsets = (
        ('基本配额', {
            'fields': ('max_users', 'max_admins', 'max_products', 'max_storage_mb')
        }),
        ('当前使用情况', {
            'fields': ('current_storage_used_mb', 'get_user_quota_status', 
                      'get_admin_quota_status', 'get_product_quota_status',
                      'get_storage_quota_status')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_quota_status(self, obj):
        if obj.is_user_quota_exceeded():
            return "❌ 超过限制"
        return "✅ 正常"
    get_user_quota_status.short_description = '用户配额状态'
    
    def get_admin_quota_status(self, obj):
        if obj.is_admin_quota_exceeded():
            return "❌ 超过限制"
        return "✅ 正常"
    get_admin_quota_status.short_description = '管理员配额状态'
    
    def get_product_quota_status(self, obj):
        if obj.is_product_quota_exceeded():
            return "❌ 超过限制"
        return "✅ 正常"
    get_product_quota_status.short_description = '产品配额状态'
    
    def get_storage_quota_status(self, obj):
        if obj.is_storage_quota_exceeded():
            return "❌ 超过限制"
        return "✅ 正常"
    get_storage_quota_status.short_description = '存储配额状态'


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'created_at', 'get_user_count', 'get_product_count', 'get_storage_usage')
    list_filter = ('status', 'is_deleted', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TenantQuotaInline]
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'status',)
        }),
        ('其他信息', {
            'fields': ('is_deleted', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_count(self, obj):
        from users.models import User
        return User.original_objects.filter(tenant=obj).count()
    get_user_count.short_description = '用户数量'
    
    def get_product_count(self, obj):
        from products.models import Product
        return Product.original_objects.filter(tenant=obj).count()
    get_product_count.short_description = '产品数量'
    
    def get_storage_usage(self, obj):
        try:
            quota = obj.quota
            return f"{quota.current_storage_used_mb:.2f} MB / {quota.max_storage_mb} MB"
        except TenantQuota.DoesNotExist:
            return "未设置"
    get_storage_usage.short_description = '存储使用情况'
