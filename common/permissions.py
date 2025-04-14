"""
权限模块
提供自定义权限类和权限检查函数
"""
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .exceptions import PermissionException


class IsAuthenticated(BasePermission):
    """
    增强版认证权限
    抛出自定义异常，以便统一处理
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True
        raise PermissionException(message="请先登录")


class IsAdminUser(BasePermission):
    """
    管理员权限
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise PermissionException(message="请先登录")
            
        if request.user.is_admin:
            return True
            
        raise PermissionException(message="需要管理员权限")


class IsMember(BasePermission):
    """
    会员权限
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise PermissionException(message="请先登录")
            
        if request.user.is_member:
            return True
            
        raise PermissionException(message="需要会员权限")


class IsOwner(BasePermission):
    """
    对象所有者权限
    要求模型有user字段，或实现get_owner方法
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            raise PermissionException(message="请先登录")
            
        # 管理员具有所有权限
        if request.user.is_admin:
            return True
            
        # 尝试获取对象的所有者
        owner = self._get_object_owner(obj)
        
        if owner == request.user:
            return True
            
        raise PermissionException(message="您没有操作此资源的权限")
    
    def _get_object_owner(self, obj):
        """
        获取对象的所有者
        :param obj: 对象
        :return: 所有者用户对象
        """
        # 如果对象有get_owner方法，则调用
        if hasattr(obj, 'get_owner') and callable(getattr(obj, 'get_owner')):
            return obj.get_owner()
        
        # 如果对象有user字段，则返回
        if hasattr(obj, 'user'):
            return obj.user
        
        # 如果对象有owner字段，则返回
        if hasattr(obj, 'owner'):
            return obj.owner
            
        # 默认返回None
        return None
