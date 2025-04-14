"""
用户模块URL配置
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 用户认证接口
    path('auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('auth/login/', views.LoginAPIView.as_view(), name='login'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('auth/refresh-token/', views.TokenRefreshAPIView.as_view(), name='refresh_token'),
    
    # 用户资料接口
    path('profile/', views.UserProfileAPIView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change_password'),
    
    # 用户管理接口 (管理员)
    path('admin/users/', views.UserManagementAPIView.as_view(), name='manage_users'),
    path('admin/users/<int:user_id>/', views.UserDetailManagementAPIView.as_view(), name='manage_user_detail'),
]
