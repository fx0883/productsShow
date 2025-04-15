"""
租户管理相关序列化器
"""
from rest_framework import serializers
from .models import Tenant, TenantQuota
from users.models import User
from products.models import Product

class TenantSerializer(serializers.ModelSerializer):
    """
    租户序列化器
    """
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TenantCreateSerializer(serializers.ModelSerializer):
    """
    创建租户序列化器
    """
    class Meta:
        model = Tenant
        fields = ['name', 'status']

    def validate_name(self, value):
        """
        验证租户名称的唯一性
        """
        if Tenant.objects.filter(name=value).exists():
            raise serializers.ValidationError("租户名称已存在")
        return value

class TenantUpdateSerializer(serializers.ModelSerializer):
    """
    更新租户序列化器
    """
    class Meta:
        model = Tenant
        fields = ['name', 'status']
        read_only_fields = ['id']

    def validate_name(self, value):
        """
        验证租户名称的唯一性（排除当前租户）
        """
        tenant_id = self.instance.id if self.instance else None
        if Tenant.objects.filter(name=value).exclude(id=tenant_id).exists():
            raise serializers.ValidationError("租户名称已存在")
        return value


class TenantDetailSerializer(serializers.ModelSerializer):
    """
    租户详情序列化器，包含统计信息
    """
    user_count = serializers.SerializerMethodField()
    admin_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'status', 'created_at', 'updated_at', 
                 'user_count', 'admin_count', 'member_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 
                           'user_count', 'admin_count', 'member_count']
    
    def get_user_count(self, obj):
        """获取租户用户总数"""
        return User.objects.filter(tenant=obj).count()
    
    def get_admin_count(self, obj):
        """获取租户管理员数量"""
        return User.objects.filter(tenant=obj, is_admin=True).count()
    
    def get_member_count(self, obj):
        """获取租户普通用户数量"""
        return User.objects.filter(tenant=obj, is_member=True).count()


class TenantQuotaSerializer(serializers.ModelSerializer):
    """
    租户配额序列化器
    """
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = TenantQuota
        fields = [
            'id', 'tenant', 'tenant_name', 'max_users', 'max_admins', 
            'max_storage_mb', 'max_products', 'current_storage_used_mb',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant_name', 'current_storage_used_mb', 'created_at', 'updated_at']


class TenantWithQuotaSerializer(TenantDetailSerializer):
    """
    带配额信息的租户详情序列化器
    """
    quota = TenantQuotaSerializer(read_only=True)
    storage_usage_percent = serializers.SerializerMethodField()
    user_usage_percent = serializers.SerializerMethodField()
    admin_usage_percent = serializers.SerializerMethodField()
    product_usage_percent = serializers.SerializerMethodField()
    
    class Meta(TenantDetailSerializer.Meta):
        fields = TenantDetailSerializer.Meta.fields + ['quota', 'storage_usage_percent', 
                                                     'user_usage_percent', 'admin_usage_percent',
                                                     'product_usage_percent']
        read_only_fields = TenantDetailSerializer.Meta.read_only_fields + ['quota', 'storage_usage_percent',
                                                                          'user_usage_percent', 'admin_usage_percent',
                                                                          'product_usage_percent']
    
    def get_storage_usage_percent(self, obj):
        """获取存储空间使用百分比"""
        try:
            quota = obj.quota
            if quota.max_storage_mb > 0:
                return round((quota.current_storage_used_mb / quota.max_storage_mb) * 100, 2)
            return 0
        except:
            return 0
    
    def get_user_usage_percent(self, obj):
        """获取用户数量使用百分比"""
        try:
            quota = obj.quota
            user_count = self.get_user_count(obj)
            if quota.max_users > 0:
                return round((user_count / quota.max_users) * 100, 2)
            return 0
        except:
            return 0
    
    def get_admin_usage_percent(self, obj):
        """获取管理员数量使用百分比"""
        try:
            quota = obj.quota
            admin_count = self.get_admin_count(obj)
            if quota.max_admins > 0:
                return round((admin_count / quota.max_admins) * 100, 2)
            return 0
        except:
            return 0
    
    def get_product_usage_percent(self, obj):
        """获取产品数量使用百分比"""
        try:
            quota = obj.quota
            product_count = Product.objects.filter(tenant=obj).count()
            if quota.max_products > 0:
                return round((product_count / quota.max_products) * 100, 2)
            return 0
        except:
            return 0
