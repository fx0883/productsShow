"""
文档视图模块
自定义的API文档视图
"""
from drf_spectacular.views import SpectacularSwaggerView

class CustomSwaggerView(SpectacularSwaggerView):
    """自定义Swagger UI视图，强制显示认证按钮"""
    
    template_name = 'swagger-ui.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取原始settings
        swagger_settings = context.get('settings', {})
        
        # 确保persistAuthorization为true
        if 'persistAuthorization' not in swagger_settings:
            swagger_settings['persistAuthorization'] = True
            
        # 确保显示认证按钮
        swagger_settings['displayRequestDuration'] = True
        swagger_settings['docExpansion'] = 'list'
        swagger_settings['filter'] = True
        
        # 更新context
        context['settings'] = swagger_settings
        
        return context
