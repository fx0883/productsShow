from django.shortcuts import render

# Create your views here.

"""
视图基类模块
提供标准化的API视图基类
"""
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, CreateAPIView, 
    UpdateAPIView, DestroyAPIView, ListCreateAPIView,
    RetrieveUpdateAPIView, RetrieveDestroyAPIView, 
    RetrieveUpdateDestroyAPIView
)

from .response import APIResponse, success_response, error_response
from .permissions import IsAuthenticated, IsAdminUser, IsMember, IsOwner
from .exceptions import BusinessException, ResourceNotFoundException
from .pagination import StandardPagination


class BaseAPIView(APIView):
    """
    API视图基类
    提供标准化的响应方法
    """
    
    def success(self, data=None, message=None, **kwargs):
        """
        成功响应
        :param data: 响应数据
        :param message: 响应消息
        :return: APIResponse
        """
        return success_response(data=data, message=message, **kwargs)
        
    def error(self, message=None, code=400, data=None, **kwargs):
        """
        错误响应
        :param message: 错误消息
        :param code: 错误码
        :param data: 错误数据
        :return: APIResponse
        """
        return error_response(message=message, code=code, data=data, **kwargs)
    
    def get_object_or_404(self, queryset, **kwargs):
        """
        获取对象，如果不存在则抛出404异常
        :param queryset: 查询集
        :param kwargs: 查询条件
        :return: 对象实例
        """
        try:
            return queryset.get(**kwargs)
        except queryset.model.DoesNotExist:
            raise ResourceNotFoundException(
                message=f"{queryset.model._meta.verbose_name}不存在"
            )


class BaseModelViewSet(ModelViewSet):
    """
    模型视图集基类
    提供标准化的响应方法
    """
    pagination_class = StandardPagination
    
    def success(self, data=None, message=None, **kwargs):
        """成功响应"""
        return success_response(data=data, message=message, **kwargs)
        
    def error(self, message=None, code=400, data=None, **kwargs):
        """错误响应"""
        return error_response(message=message, code=code, data=data, **kwargs)


class BaseReadOnlyModelViewSet(ReadOnlyModelViewSet):
    """
    只读模型视图集基类
    提供标准化的响应方法
    """
    pagination_class = StandardPagination
    
    def success(self, data=None, message=None, **kwargs):
        """成功响应"""
        return success_response(data=data, message=message, **kwargs)
        
    def error(self, message=None, code=400, data=None, **kwargs):
        """错误响应"""
        return error_response(message=message, code=code, data=data, **kwargs)


class BaseListAPIView(ListAPIView):
    """列表视图基类"""
    pagination_class = StandardPagination
    
    def get_paginated_response(self, data):
        """重写分页响应"""
        return self.paginator.get_paginated_response(data)


class BaseRetrieveAPIView(RetrieveAPIView):
    """详情视图基类"""
    pass


class BaseCreateAPIView(CreateAPIView):
    """创建视图基类"""
    pass


class BaseUpdateAPIView(UpdateAPIView):
    """更新视图基类"""
    pass


class BaseDestroyAPIView(DestroyAPIView):
    """删除视图基类"""
    pass


class BaseListCreateAPIView(ListCreateAPIView):
    """列表创建视图基类"""
    pagination_class = StandardPagination


class BaseRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """详情更新删除视图基类"""
    pass
