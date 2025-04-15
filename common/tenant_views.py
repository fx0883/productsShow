"""
租户管理视图
提供租户的创建、查询、修改和删除功能
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    TenantSerializer, 
    TenantCreateSerializer, 
    TenantUpdateSerializer,
    TenantDetailSerializer,
    TenantWithQuotaSerializer,
    TenantQuotaSerializer
)
from .models import Tenant, TenantQuota
from .views import BaseAPIView, BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
from users.authentication import JWTAuthentication
from common.permissions import IsAuthenticated, IsSuperAdminUser, IsAdminUser
from users.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from django.db.models import Q
from django.db import models
from datetime import datetime
from .api_examples import (
    tenant_list_response_example,
    tenant_create_request_example,
    tenant_create_response_example,
    tenant_create_400_example,
    tenant_detail_response_example,
    tenant_update_request_example,
    tenant_update_response_example,
    tenant_update_400_example,
    tenant_delete_response_example,
    tenant_not_found_example,
    tenant_user_list_response_example,
    tenant_user_list_400_example,
    tenant_quota_request_example,
    tenant_quota_response_example,
    tenant_quota_update_response_example,
    tenant_quota_update_400_example,
)


class TenantListCreateAPIView(BaseListCreateAPIView):
    """
    租户列表和创建API
    
    list:
    获取所有租户列表
    
    create:
    创建新租户
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdminUser]
    serializer_class = TenantSerializer
    queryset = Tenant.objects.all()
    
    @extend_schema(
        tags=['租户管理'],
        summary="获取租户列表",
        description="获取系统中所有租户的列表，仅超级管理员可访问",
        responses={
            200: OpenApiResponse(
                description="成功响应",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_list_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
        },
        auth=[{"Bearer": []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        tags=['租户管理'],
        summary="创建新租户",
        description="创建一个新的租户，仅超级管理员可访问",
        request=TenantCreateSerializer,
        examples=[
            OpenApiExample(
                name='创建租户请求',
                value=tenant_create_request_example,
                request_only=True,
            )
        ],
        responses={
            200: OpenApiResponse(
                description="成功响应",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_create_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="创建失败",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_create_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TenantCreateSerializer
        return TenantSerializer
    
    def perform_create(self, serializer):
        """
        创建租户
        """
        serializer.save()
        return self.success(data=serializer.data, message="租户创建成功")


class TenantDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    """
    租户详情API
    
    retrieve:
    获取租户详情
    
    update:
    更新租户信息
    
    destroy:
    删除租户（软删除）
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdminUser]
    serializer_class = TenantSerializer
    queryset = Tenant.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'tenant_id'
    
    @extend_schema(
        tags=['租户管理'],
        summary="获取租户详情",
        description="获取指定租户的详细信息，包括配额使用情况",
        responses={
            200: OpenApiResponse(
                description="成功响应",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_detail_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="租户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_not_found_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        tags=['租户管理'],
        summary="更新租户信息",
        description="更新指定租户的信息",
        request=TenantUpdateSerializer,
        examples=[
            OpenApiExample(
                name='更新租户请求',
                value=tenant_update_request_example,
                request_only=True,
            )
        ],
        responses={
            200: OpenApiResponse(
                description="成功响应",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_update_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="更新失败",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_update_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="租户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_not_found_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        tags=['租户管理'],
        summary="删除租户",
        description="删除指定租户（软删除，仅将状态更改为已删除）",
        responses={
            200: OpenApiResponse(
                description="成功响应",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_delete_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="租户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_not_found_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            # 使用带配额信息的详情序列化器
            return TenantWithQuotaSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return TenantUpdateSerializer
        return TenantSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        获取租户详情，确保返回的信息包含配额信息
        """
        tenant = self.get_object()
        
        # 确保租户有配额设置
        quota, created = TenantQuota.objects.get_or_create(tenant=tenant)
        
        # 如果是新创建的配额，更新存储使用情况
        if created or quota.updated_at.date() < datetime.now().date():
            quota.update_storage_usage()
        
        serializer = self.get_serializer(tenant)
        return self.success(data=serializer.data, message="获取租户详情成功")
    
    def perform_update(self, serializer):
        """
        更新租户
        """
        serializer.save()
        return self.success(data=serializer.data, message="租户更新成功")
    
    def destroy(self, request, *args, **kwargs):
        """
        软删除租户
        """
        tenant = self.get_object()
        # 软删除，更新状态为已删除
        tenant.status = 'deleted'
        tenant.save()
        
        return self.success(message="租户删除成功")


class TenantUserListAPIView(BaseAPIView):
    """
    租户用户列表API
    
    GET:
    获取指定租户的用户列表（超级管理员）或当前租户的用户列表（租户管理员）
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        tags=['租户管理'],
        summary="获取租户用户列表",
        description="获取租户下所有用户，超级管理员可以查看任意租户，租户管理员只能查看自己租户",
        parameters=[
            OpenApiParameter(name='tenant_id', description='租户ID（超级管理员必填，租户管理员可选）', required=False, type=int),
            OpenApiParameter(name='page', description='页码', required=False, type=int, default=1),
            OpenApiParameter(name='page_size', description='每页数量', required=False, type=int, default=10),
            OpenApiParameter(name='search', description='搜索关键词（用户名或邮箱）', required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(
                description="成功响应",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_user_list_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="请求参数错误",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_user_list_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}]
    )
    def get(self, request):
        """获取租户用户列表"""
        # 超级管理员可以查看任意租户，租户管理员只能查看自己租户
        tenant_id = request.query_params.get('tenant_id')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        search = request.query_params.get('search', '')
        
        # 获取当前用户
        user = request.user
        
        # 确定查询的租户
        if user.is_super_admin:
            # 超级管理员必须指定租户ID
            if not tenant_id:
                return self.error(
                    message="超级管理员必须指定租户ID",
                    code=1018,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            try:
                tenant = Tenant.objects.get(id=tenant_id)
            except Tenant.DoesNotExist:
                return self.error(
                    message="租户不存在",
                    code=1013,
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # 普通管理员只能查看自己的租户
            tenant = user.tenant
            if not tenant:
                return self.error(
                    message="您未关联到任何租户",
                    code=1014,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # 查询租户下的用户
        queryset = User.objects.filter(tenant=tenant)
        
        # 应用搜索
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | 
                Q(email__icontains=search) |
                Q(nick_name__icontains=search)
            )
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        users = queryset[start:end]
        
        # 整理用户数据
        user_data = []
        for u in users:
            user_data.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'nick_name': u.nick_name,
                'is_admin': u.is_admin,
                'is_member': u.is_member,
                'is_super_admin': u.is_super_admin,
                'created_at': u.date_joined
            })
        
        # 构建响应数据
        data = {
            'tenant': {
                'id': tenant.id,
                'name': tenant.name,
                'status': tenant.status
            },
            'users': {
                'count': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'results': user_data
            }
        }
        
        return self.success(data=data, message="获取租户用户列表成功")


class TenantQuotaAPIView(BaseAPIView):
    """
    租户配额管理API
    
    GET:
    获取指定租户的配额信息
    
    PUT:
    更新指定租户的配额信息
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdminUser]
    
    @extend_schema(
        tags=['租户管理'],
        summary="获取租户配额信息",
        description="获取指定租户的配额设置及使用情况",
        parameters=[
            OpenApiParameter(name='tenant_id', description='租户ID', required=True, type=int),
        ],
        responses={
            200: OpenApiResponse(
                description="成功响应",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_quota_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="租户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_not_found_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}]
    )
    def get(self, request):
        """获取租户配额信息"""
        tenant_id = request.query_params.get('tenant_id')
        
        if not tenant_id:
            return self.error(
                message="租户ID不能为空",
                code=1015,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return self.error(
                message="租户不存在",
                code=1013,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 确保租户有配额设置，如果没有则创建
        quota, created = TenantQuota.objects.get_or_create(tenant=tenant)
        
        # 更新存储使用统计（可能比较耗时，实际项目中可以考虑异步更新）
        quota.update_storage_usage()
        
        serializer = TenantQuotaSerializer(quota)
        
        return self.success(data=serializer.data, message="获取租户配额成功")
    
    @extend_schema(
        tags=['租户管理'],
        summary="更新租户配额信息",
        description="更新指定租户的配额设置",
        request=TenantQuotaSerializer,
        examples=[
            OpenApiExample(
                name='更新租户配额请求',
                value=tenant_quota_request_example,
                request_only=True,
            )
        ],
        responses={
            200: OpenApiResponse(
                description="成功响应",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_quota_update_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="参数错误",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_quota_update_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="租户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=tenant_not_found_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}]
    )
    def put(self, request):
        """更新租户配额信息"""
        tenant_id = request.data.get('tenant')
        
        if not tenant_id:
            return self.error(
                message="租户ID不能为空",
                code=1015,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return self.error(
                message="租户不存在",
                code=1013,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 获取或创建租户配额
        quota, created = TenantQuota.objects.get_or_create(tenant=tenant)
        
        # 更新配额设置
        serializer = TenantQuotaSerializer(quota, data=request.data, partial=True)
        if not serializer.is_valid():
            return self.error(
                message="参数错误",
                code=1016,
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return self.success(data=serializer.data, message="更新租户配额成功")
