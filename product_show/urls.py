"""
URL configuration for product_show project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

# API版本前缀
API_V1_PREFIX = 'api/v1/'

# OpenAPI文档配置
# schema_view = get_schema_view(
#    title="Products Show API",
#    description="Products Show API文档",
#    version="1.0.0",
#    public=True,
#    permission_classes=[AllowAny],
# )

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),
    
    # 用户模块
    path(f'{API_V1_PREFIX}users/', include('users.urls')),
    
    # 通用模块（包含租户管理）
    path(f'{API_V1_PREFIX}common/', include('common.urls')),
    
    # 其他应用
    path('doclist/', include('docs.urls')),  # 文档应用路径改为/doclist
    
    # API认证
    path('api-auth/', include('rest_framework.urls')),
    
    # OpenAPI文档 - drf-spectacular
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    
    # Swagger UI (简化配置，专注于解决认证按钮问题)
    path('api/swagger/', SpectacularSwaggerView.as_view(
        url_name='schema',
        permission_classes=[AllowAny],
    ), name='swagger-ui'),
    
    # ReDoc UI
    path('api/redoc/', SpectacularRedocView.as_view(
        url_name='schema',
        permission_classes=[AllowAny],
    ), name='redoc'),
]

# 在开发模式下添加静态文件服务
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
