"""
Common应用URL配置
"""
from django.urls import path
from . import tenant_views

app_name = 'common'

urlpatterns = [
    # 租户管理接口
    path('tenants/', tenant_views.TenantListCreateAPIView.as_view(), name='tenant_list'),
    path('tenants/users/', tenant_views.TenantUserListAPIView.as_view(), name='tenant_user_list'),
    path('tenants/quota/', tenant_views.TenantQuotaAPIView.as_view(), name='tenant_quota'),
    path('tenants/<int:tenant_id>/', tenant_views.TenantDetailAPIView.as_view(), name='tenant_detail'),
]
