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


class BaseListCreateAPIView(ListCreateAPIView, BaseAPIView):
    """列表创建视图基类"""
    pagination_class = StandardPagination
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
                
            serializer = self.get_serializer(queryset, many=True)
            return self.success(data=serializer.data, message="获取列表成功")
        except Exception as e:
            return self.error(message=str(e), code=1001)
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer)
            
            # 如果perform_create返回了实例，使用它获取数据，否则使用序列化器的数据
            if instance:
                serializer = self.get_serializer(instance)
                
            return self.success(
                data=serializer.data, 
                message="创建成功",
                status_code=200  # 确保使用200而不是201
            )
        except Exception as e:
            return self.error(message=str(e), code=1002)


class BaseRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, BaseAPIView):
    """详情更新删除视图基类"""
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success(data=serializer.data, message="获取详情成功")
        except Exception as e:
            return self.error(message=str(e), code=1003)
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return self.success(data=serializer.data, message="更新成功")
        except Exception as e:
            return self.error(message=str(e), code=1004)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return self.success(message="删除成功")
        except Exception as e:
            return self.error(message=str(e), code=1005)
