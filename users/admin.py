from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from .models import User, UserProfile, UserToken

# Register your models here.

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fieldsets = (
        ('个人设置', {
            'fields': ('preferred_language', 'date_format')
        }),
    )

class UserAdmin(BaseUserAdmin):
    # 自动获取所有字段并添加额外的方法字段，但排除password
    def get_list_display(self, request):
        default_fields = [field.name for field in User._meta.fields if field.name != 'password']
        # 添加额外的方法字段
        method_fields = ['get_tenant_name', 'get_avatar_preview']
        return default_fields + method_fields
    
    # 设置可点击字段
    list_display_links = ['id', 'username']
    
    list_filter = ('is_super_admin', 'is_admin', 'is_member', 'is_active', 'is_staff', 'is_superuser', 'tenant')
    search_fields = ('username', 'email', 'phone', 'nick_name', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'get_avatar_preview')
    filter_horizontal = ('user_permissions', 'groups')
    
    # 手动定义fieldsets以确保所有字段都包含，特别是自定义字段
    fieldsets = (
        ('账户信息', {
            'fields': ('username', 'email', 'phone', 'password')
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'nick_name', 'avatar', 'get_avatar_preview')
        }),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_super_admin', 'is_admin', 'is_member',
                      'groups', 'user_permissions')
        }),
        ('租户信息', {
            'fields': ('tenant',)
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # 添加用户时的字段集
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'nick_name', 'avatar', 'password1', 'password2', 'tenant', 
                      'is_staff', 'is_superuser', 'is_super_admin', 'is_admin', 'is_member')
        }),
    )
    
    inlines = [UserProfileInline]

    def get_tenant_name(self, obj):
        return obj.tenant.name if obj.tenant else '未分配'
    get_tenant_name.short_description = '租户'
    get_tenant_name.admin_order_field = 'tenant__name'
    
    def get_avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.avatar.url)
        return "无头像"
    get_avatar_preview.short_description = "头像预览"
    
    # 确保所有用户都可编辑
    def has_change_permission(self, request, obj=None):
        return True

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token_type', 'is_valid', 'expired_at', 'created_at', 'is_expired')
    list_filter = ('token_type', 'is_valid', 'expired_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'is_expired')
    fieldsets = (
        ('令牌信息', {
            'fields': ('user', 'token', 'token_type', 'is_valid', 'expired_at')
        }),
        ('其他信息', {
            'fields': ('created_at', 'is_expired'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = '是否过期'

# 注册模型
admin.site.register(User, UserAdmin)
# 如果需要Group模型，取消下面的注释
# admin.site.unregister(Group)
