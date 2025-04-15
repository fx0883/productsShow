from django.shortcuts import render
from django.contrib.auth import login, logout
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.conf import settings

# 移除drf-yasg导入
# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema

# 添加drf-spectacular导入
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from common.views import BaseAPIView
from common.exceptions import BusinessException, AuthenticationException
from common.permissions import IsAuthenticated, IsAdminUser, IsSuperAdminUser
from common.models import Tenant, TenantQuota

from .models import User, UserToken
from .serializers import (
    UserRegisterSerializer, 
    UserLoginSerializer, 
    UserSerializer, 
    UserDetailSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
    TokenRefreshSerializer,
    ResetPasswordSerializer,
    UserTenantAssignSerializer,  # 添加用户租户分配序列化器
    TenantUserCreateSerializer  # 添加租户用户创建序列化器
)
from .authentication import JWTAuthentication, TokenManager
from .api_examples import *  # 导入API示例数据


# 添加一个用于文档的辅助函数
def get_token_auth_header():
    """用于Swagger中测试时添加认证令牌的函数"""
    return {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...（这里是您的访问令牌）'}

class RegisterAPIView(BaseAPIView):
    """用户注册API"""
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @extend_schema(
        tags=['认证'],
        summary="用户注册",
        description="创建新用户账号",
        request=UserRegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
                description="注册成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=register_response_example,
                        status_codes=['201'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="请求参数错误",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=register_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='注册请求',
                value=register_request_example,
                request_only=True,
            )
        ]
    )
    def post(self, request):
        """处理用户注册请求"""
        try:
            serializer = UserRegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # 生成令牌
                try:
                    access_token, refresh_token, _, _ = TokenManager.generate_tokens(user)
                    
                    # 返回用户信息和令牌
                    return self.success(
                        data={
                            'user': UserSerializer(user).data,
                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'token_type': 'Bearer'
                        },
                        message="注册成功",
                        status_code=status.HTTP_201_CREATED
                    )
                except Exception as e:
                    # 使用改进的错误处理
                    return self.error(
                        message="令牌生成失败",
                        code=1001,
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        exception_obj=e
                    )
            
            return self.error(
                data=serializer.errors,
                message="注册失败，请检查输入",
                code=1001,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # 使用改进的错误处理
            return self.error(
                message="注册处理失败",
                code=1001,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                exception_obj=e
            )


class LoginAPIView(BaseAPIView):
    """用户登录API"""
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @extend_schema(
        tags=['认证'],
        summary="用户登录",
        description="使用用户名/邮箱和密码登录",
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="登录成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=login_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="用户名或密码错误",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=login_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='使用用户名登录',
                value=login_request_example,
                request_only=True,
            ),
            OpenApiExample(
                name='使用邮箱登录',
                value=login_with_email_example,
                request_only=True,
            )
        ]
    )
    def post(self, request):
        """处理用户登录请求"""
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Django会话登录（可选）
            login(request, user)
            
            # 生成令牌
            access_token, refresh_token, _, _ = TokenManager.generate_tokens(user)
            
            # 更新最后登录时间
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # 返回用户信息和令牌
            return self.success(
                data={
                    'user': UserSerializer(user).data,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer'
                },
                message="登录成功"
            )
        
        return self.error(
            data=serializer.errors,
            message="登录失败，请检查用户名和密码",
            code=1002,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class LogoutAPIView(BaseAPIView):
    """用户登出API"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @extend_schema(
        tags=['认证'],
        summary="用户登出",
        description="使当前用户的所有令牌失效",
        responses={
            200: OpenApiResponse(
                description="登出成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=logout_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}],
        examples=[
            
        ]
    )
    def post(self, request):
        """处理用户登出请求"""
        # Django会话登出（可选）
        logout(request)
        
        # 使所有令牌失效
        if hasattr(request, 'user') and request.user.is_authenticated:
            TokenManager.invalidate_user_tokens(request.user)
        
        return self.success(message="登出成功")


class TokenRefreshAPIView(BaseAPIView):
    """令牌刷新API"""
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @extend_schema(
        tags=['认证'],
        summary="刷新访问令牌",
        description="使用刷新令牌获取新的访问令牌",
        request=TokenRefreshSerializer,
        responses={
            200: OpenApiResponse(
                description="令牌刷新成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=refresh_token_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="刷新令牌无效",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=refresh_token_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='刷新令牌请求',
                value=refresh_token_request_example,
                request_only=True,
            )
        ]
    )
    def post(self, request):
        """处理令牌刷新请求"""
        serializer = TokenRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error(
                data=serializer.errors,
                message="刷新令牌不能为空",
                code=1003,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        refresh_token = serializer.validated_data['refresh_token']
        
        try:
            # 验证刷新令牌
            user, _, _ = TokenManager.verify_token(refresh_token, is_refresh=True)
            
            # 吊销旧令牌
            TokenManager.invalidate_token(refresh_token)
            
            # 生成新令牌
            access_token, new_refresh_token, _, _ = TokenManager.generate_tokens(user)
            
            # 返回新令牌
            return self.success(
                data={
                    'access_token': access_token,
                    'refresh_token': new_refresh_token,
                    'token_type': 'Bearer'
                },
                message="令牌刷新成功"
            )
        except Exception as e:
            return self.error(
                message=str(e) if str(e) else "无效的刷新令牌",
                code=1003,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class UserProfileAPIView(BaseAPIView):
    """用户资料API"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @extend_schema(
        tags=['用户'],
        summary="获取用户资料",
        description="获取当前登录用户的详细资料",
        responses={
            200: OpenApiResponse(
                response=UserDetailSerializer,
                description="获取成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=user_profile_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}],
        examples=[
            
        ]
    )
    def get(self, request):
        """获取用户资料"""
        serializer = UserDetailSerializer(request.user)
        return self.success(data=serializer.data, message="获取用户资料成功")
    
    @extend_schema(
        tags=['用户'],
        summary="更新用户资料",
        description="更新当前登录用户的资料",
        request=UserDetailSerializer,
        responses={
            200: OpenApiResponse(
                response=UserDetailSerializer,
                description="更新成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=user_profile_update_response_example,
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
                        value=user_profile_update_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='更新用户资料请求',
                value=user_profile_update_request_example,
                request_only=True,
            )
        ],
        auth=[{"Bearer": []}]
    )
    def put(self, request):
        """更新用户资料"""
        user = request.user
        user_data = request.data.copy()
        profile_data = user_data.pop('profile', {})
        
        # 更新用户数据
        user_serializer = UserDetailSerializer(user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            
            # 更新用户配置
            if profile_data:
                profile_serializer = UserProfileSerializer(user.profile, data=profile_data, partial=True)
                if profile_serializer.is_valid():
                    profile_serializer.save()
                else:
                    return self.error(
                        data=profile_serializer.errors,
                        message="用户配置更新失败",
                        code=1005,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            # 返回更新后的完整用户资料
            serializer = UserDetailSerializer(user)
            return self.success(data=serializer.data, message="用户资料更新成功")
            
        return self.error(
            data=user_serializer.errors,
            message="用户资料更新失败",
            code=1006,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordAPIView(BaseAPIView):
    """修改密码API"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @extend_schema(
        tags=['认证'],
        summary="修改密码",
        description="修改当前登录用户的密码",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="修改成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=change_password_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="请求参数错误或旧密码不正确",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=change_password_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='修改密码请求',
                value=change_password_request_example,
                request_only=True,
            )
        ],
        auth=[{"Bearer": []}]
    )
    def post(self, request):
        """处理修改密码请求"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # 验证旧密码
            if not request.user.check_password(serializer.validated_data['old_password']):
                return self.error(
                    message="旧密码不正确",
                    code=1007,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # 设置新密码
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            # 使所有现有令牌失效
            TokenManager.invalidate_user_tokens(request.user)
            
            # 生成新令牌
            access_token, refresh_token, _, _ = TokenManager.generate_tokens(request.user)
            
            return self.success(
                data={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer'
                },
                message="密码修改成功"
            )
            
        return self.error(
            data=serializer.errors,
            message="密码修改失败",
            code=1008,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UserManagementAPIView(BaseAPIView):
    """用户管理API（仅管理员可用）"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [JWTAuthentication]
    
    @extend_schema(
        tags=['管理员'],
        summary="获取用户列表",
        description="获取所有用户的列表（管理员接口）",
        responses={
            200: OpenApiResponse(
                response=UserSerializer(many=True),
                description="获取成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=user_list_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}],
        examples=[
            
        ]
    )
    def get(self, request):
        """获取所有用户列表"""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return self.success(data=serializer.data, message="获取用户列表成功")
    
    @extend_schema(
        tags=['管理员'],
        summary="创建用户",
        description="创建新用户（管理员接口）",
        request=UserRegisterSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="创建成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=create_user_response_example,
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
                        value=create_user_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='创建用户请求',
                value=create_user_request_example,
                request_only=True,
            )
        ],
        auth=[{"Bearer": []}]
    )
    def post(self, request):
        """创建新用户"""
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return self.success(
                data=UserSerializer(user).data,
                message="用户创建成功",
                status_code=status.HTTP_200_OK
            )
        
        return self.error(
            data=serializer.errors,
            message="用户创建失败",
            code=1009,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UserDetailManagementAPIView(BaseAPIView):
    """用户详情管理API（仅管理员可用）"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [JWTAuthentication]
    
    @extend_schema(
        tags=['管理员'],
        summary="获取用户详情",
        description="获取指定用户的详细信息（管理员接口）",
        responses={
            200: OpenApiResponse(
                response=UserDetailSerializer,
                description="获取成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=user_detail_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="用户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=user_detail_404_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}],
        examples=[
            
        ]
    )
    def get(self, request, user_id):
        """获取指定用户详情"""
        try:
            user = User.objects.get(id=user_id)
            serializer = UserDetailSerializer(user)
            return self.success(data=serializer.data, message="获取用户详情成功")
        except User.DoesNotExist:
            return self.error(
                message="用户不存在",
                code=1010,
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['管理员'],
        summary="更新用户",
        description="更新指定用户的信息（管理员接口）",
        request=UserDetailSerializer,
        responses={
            200: OpenApiResponse(
                response=UserDetailSerializer,
                description="更新成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=update_user_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="用户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=update_user_404_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="请求参数错误",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=update_user_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='更新用户请求',
                value=update_user_request_example,
                request_only=True,
            )
        ],
        auth=[{"Bearer": []}]
    )
    def put(self, request, user_id):
        """更新指定用户信息"""
        try:
            user = User.objects.get(id=user_id)
            user_data = request.data.copy()
            profile_data = user_data.pop('profile', {})
            
            # 更新用户数据
            user_serializer = UserDetailSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
                
                # 更新用户配置
                if profile_data:
                    profile_serializer = UserProfileSerializer(user.profile, data=profile_data, partial=True)
                    if profile_serializer.is_valid():
                        profile_serializer.save()
                    else:
                        return self.error(
                            data=profile_serializer.errors,
                            message="用户配置更新失败",
                            code=1011,
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                
                # 返回更新后的完整用户资料
                serializer = UserDetailSerializer(user)
                return self.success(data=serializer.data, message="用户信息更新成功")
                
            return self.error(
                data=user_serializer.errors,
                message="用户信息更新失败",
                code=1012,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except User.DoesNotExist:
            return self.error(
                message="用户不存在",
                code=1013,
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['管理员'],
        summary="删除用户",
        description="删除指定用户（管理员接口）",
        responses={
            200: OpenApiResponse(
                description="删除成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=delete_user_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="用户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=delete_user_404_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}],
        examples=[
            OpenApiExample(
                name='删除用户请求',
                value=get_token_auth_header(),
                request_only=True,
            )
        ]
    )
    def delete(self, request, user_id):
        """删除指定用户"""
        try:
            user = User.objects.get(id=user_id)
            
            # 不允许删除自己
            if user.id == request.user.id:
                return self.error(
                    message="不能删除当前登录的用户",
                    code=1014,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            # 删除用户
            user.delete()
            
            return self.success(message="用户删除成功")
            
        except User.DoesNotExist:
            return self.error(
                message="用户不存在",
                code=1015,
                status_code=status.HTTP_404_NOT_FOUND
            )


class DeleteUserAPIView(BaseAPIView):
    """删除用户视图"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        tags=['管理员'],
        summary="删除用户",
        description="管理员删除指定用户",
        responses={
            200: OpenApiResponse(
                description="删除成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=delete_user_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}],
        examples=[
            OpenApiExample(
                name='删除用户请求',
                value=get_token_auth_header(),
                request_only=True,
            )
        ]
    )
    def delete(self, request, user_id):
        """删除用户"""
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return self.success(message="用户删除成功")
        except User.DoesNotExist:
            return self.error(message="用户不存在", code=1016)


class UserDetailUpdateAPIView(BaseAPIView):
    """用户详情更新视图"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        tags=['管理员'],
        summary="更新用户信息",
        description="管理员更新指定用户信息",
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                response=UserDetailSerializer,
                description="更新成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=update_user_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            )
        },
        auth=[{"Bearer": []}],
        examples=[
            OpenApiExample(
                name='更新用户信息请求',
                value=get_token_auth_header(),
                request_only=True,
            )
        ]
    )
    def put(self, request, user_id):
        """更新用户信息"""
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success(message="用户信息更新成功")
            return self.error(message=serializer.errors, code=1017)
        except User.DoesNotExist:
            return self.error(message="用户不存在", code=1018)


class ResetPasswordAPIView(BaseAPIView):
    """密码重置API - 使用超级密钥"""
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @extend_schema(
        tags=['工具'],
        summary="重置用户密码",
        description="使用超级密钥重置指定用户的密码为默认密码(123456)",
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="重置成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=reset_password_response_example,
                        status_codes=['200'],
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="超级密钥不正确",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=reset_password_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            ),
            404: OpenApiResponse(
                description="用户不存在",
                examples=[
                    OpenApiExample(
                        name='错误响应',
                        value=reset_password_404_example,
                        status_codes=['404'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='重置密码请求',
                value=reset_password_request_example,
                request_only=True,
            )
        ]
    )
    def post(self, request):
        """处理密码重置请求"""
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # 验证超级密钥
            super_key = serializer.validated_data['super_key']
            if super_key != settings.RESET_PASSWORD_SUPER_KEY:
                return self.error(
                    message="超级密钥不正确",
                    code=1011,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # 查找用户
            user_id = serializer.validated_data['user_id']
            try:
                user = User.objects.get(id=user_id)
                
                # 重置密码为默认值
                default_password = '123456'
                user.set_password(default_password)
                user.save()
                
                # 使所有现有令牌失效
                TokenManager.invalidate_user_tokens(user)
                
                return self.success(
                    data={
                        'user_id': user.id,
                        'username': user.username
                    },
                    message=f"密码重置成功，新密码为: {default_password}"
                )
                
            except User.DoesNotExist:
                return self.error(
                    message="用户不存在",
                    code=4041,
                    status_code=status.HTTP_404_NOT_FOUND
                )
                
        return self.error(
            data=serializer.errors,
            message="密码重置失败，请检查输入",
            code=1012,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UserTenantAssignAPIView(BaseAPIView):
    """用户租户分配API"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdminUser]
    
    @extend_schema(
        tags=['管理员'],
        summary="用户租户分配",
        description="将用户分配到指定租户",
        request=UserTenantAssignSerializer,
        responses={
            200: OpenApiResponse(
                description="分配成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=user_tenant_assign_response_example,
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
                        value=user_tenant_assign_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='用户租户分配请求',
                value=user_tenant_assign_request_example,
                request_only=True,
            )
        ],
        auth=[{"Bearer": []}]
    )
    def post(self, request):
        """处理用户租户分配请求"""
        from common.models import Tenant
        
        serializer = UserTenantAssignSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            tenant_id = serializer.validated_data['tenant_id']
            
            try:
                user = User.objects.get(id=user_id)
                tenant = Tenant.objects.get(id=tenant_id)
            except User.DoesNotExist:
                return self.error(
                    message="用户不存在",
                    code=1012,
                    status_code=status.HTTP_404_NOT_FOUND
                )
            except Tenant.DoesNotExist:
                return self.error(
                    message="租户不存在",
                    code=1013,
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # 更新用户所属租户
            user.tenant = tenant
            user.save()
            
            # 使所有该用户的令牌失效，强制用户重新登录
            UserToken.objects.filter(user=user).update(is_valid=False)
            
            return self.success(
                data={
                    "user_id": user.id, 
                    "username": user.username,
                    "tenant_id": tenant.id,
                    "tenant_name": tenant.name
                },
                message="用户租户分配成功"
            )
            
        return self.error(
            data=serializer.errors,
            message="用户租户分配失败",
            code=1010,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class TenantUserCreateAPIView(BaseAPIView):
    """租户内用户创建API"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        tags=['租户管理'],
        summary="创建租户内用户",
        description="租户管理员可以在自己的租户内创建用户",
        request=TenantUserCreateSerializer,
        responses={
            200: OpenApiResponse(
                description="创建成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=tenant_user_create_response_example,
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
                        value=tenant_user_create_400_example,
                        status_codes=['400'],
                        response_only=True,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='创建租户内用户请求',
                value=tenant_user_create_request_example,
                request_only=True,
            )
        ],
        auth=[{"Bearer": []}]
    )
    def post(self, request):
        """处理租户内用户创建请求"""
        try:
            serializer = TenantUserCreateSerializer(data=request.data)
            if serializer.is_valid():
                # 获取当前用户的租户
                current_tenant = request.user.tenant
                
                # 超级管理员可以指定租户
                if request.user.is_super_admin and 'tenant_id' in request.data:
                    try:
                        tenant_id = request.data.get('tenant_id')
                        current_tenant = Tenant.objects.get(id=tenant_id)
                    except Tenant.DoesNotExist:
                        return self.error(
                            message="指定的租户不存在",
                            code=1019,
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                
                if not current_tenant:
                    return self.error(
                        message="您未关联到任何租户",
                        code=1014,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # 检查当前用户是否有权限创建用户
                # 只有租户管理员或超级管理员可以创建用户
                if not (request.user.is_admin or request.user.is_super_admin):
                    return self.error(
                        message="您没有权限创建用户",
                        code=1015,
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                
                # 普通管理员只能在自己的租户内创建用户
                if not request.user.is_super_admin and serializer.validated_data.get('is_super_admin'):
                    return self.error(
                        message="您没有权限创建超级管理员",
                        code=1016,
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                
                # 检查配额限制
                quota, created = TenantQuota.objects.get_or_create(tenant=current_tenant)
                if quota.is_user_quota_exceeded():
                    return self.error(
                        message=f"租户用户配额已达上限({quota.max_users}个用户)",
                        code=1020,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # 创建用户
                user = serializer.save(tenant=current_tenant, is_super_admin=False)
                
                # 设置密码
                user.set_password(serializer.validated_data['password'])
                user.save()
                
                return self.success(
                    data={
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "is_admin": user.is_admin,
                        "is_member": user.is_member,
                        "tenant_id": current_tenant.id,
                        "tenant_name": current_tenant.name
                    },
                    message="用户创建成功",
                    status_code=status.HTTP_200_OK
                )
                
            return self.error(
                data=serializer.errors,
                message="用户创建失败",
                code=1017,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return self.error(
                message=f"创建用户失败: {str(e)}",
                code=1018,
                status_code=status.HTTP_400_BAD_REQUEST
            )
