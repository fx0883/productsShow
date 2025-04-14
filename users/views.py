from django.shortcuts import render
from django.contrib.auth import login, logout
from django.utils import timezone
from django.utils.decorators import method_decorator

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
from common.permissions import IsAdminUser

from .models import User, UserToken
from .serializers import (
    UserRegisterSerializer, 
    UserLoginSerializer, 
    UserSerializer, 
    UserDetailSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
    TokenRefreshSerializer
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
            OpenApiExample(
                name='登出请求',
                value=get_token_auth_header(),
                request_only=True,
            )
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
            201: OpenApiResponse(
                response=UserSerializer,
                description="创建成功",
                examples=[
                    OpenApiExample(
                        name='成功响应',
                        value=create_user_response_example,
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
                status_code=status.HTTP_201_CREATED
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
            OpenApiExample(
                name='获取用户详情请求',
                value=get_token_auth_header(),
                request_only=True,
            )
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
            ),
            OpenApiExample(
                name='更新用户请求',
                value=get_token_auth_header(),
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
            user_serializer = UserSerializer(user, data=user_data, partial=True)
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
