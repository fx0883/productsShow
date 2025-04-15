"""
租户中间件模块
提供租户上下文管理和请求处理中间件
"""
import threading
from django.utils.deprecation import MiddlewareMixin


# 线程本地存储，用于存储当前请求的租户信息
_thread_local = threading.local()


def get_current_tenant():
    """
    获取当前线程的租户
    :return: Tenant实例或None
    """
    return getattr(_thread_local, 'tenant', None)


def set_current_tenant(tenant):
    """
    设置当前线程的租户
    :param tenant: Tenant实例
    """
    _thread_local.tenant = tenant


def clear_current_tenant():
    """
    清除当前线程的租户
    """
    if hasattr(_thread_local, 'tenant'):
        del _thread_local.tenant


class TenantMiddleware(MiddlewareMixin):
    """
    租户中间件
    负责从请求中提取租户信息并设置到线程本地存储
    """
    
    def process_request(self, request):
        """
        处理请求，设置当前租户
        :param request: HttpRequest实例
        """
        # 清除之前的租户信息
        clear_current_tenant()
        
        # 获取当前用户
        user = request.user
        
        # 如果用户已认证，设置其所属租户
        if user and user.is_authenticated:
            set_current_tenant(user.tenant)
            
        return None
    
    def process_response(self, request, response):
        """
        处理响应，清除租户信息
        :param request: HttpRequest实例
        :param response: HttpResponse实例
        :return: HttpResponse实例
        """
        # 清除租户信息
        clear_current_tenant()
        
        return response
    
    
class TenantQuerySetMixin:
    """
    租户查询集混入类
    自动根据当前租户过滤查询结果
    """
    
    def get_queryset(self):
        """
        获取查询集，根据当前租户过滤
        如果用户是超级管理员，则不过滤
        :return: 过滤后的查询集
        """
        queryset = super().get_queryset()
        
        # 获取当前用户
        user = self.request.user
        
        # 如果用户未认证，返回空查询集
        if not user.is_authenticated:
            return queryset.none()
        
        # 如果用户是超级管理员，则不过滤
        if user.is_super_admin:
            return queryset
        
        # 获取当前租户
        tenant = get_current_tenant()
        
        # 如果没有租户，返回空查询集
        if not tenant:
            return queryset.none()
        
        # 过滤查询集，只返回当前租户的数据
        return queryset.filter(tenant=tenant)
