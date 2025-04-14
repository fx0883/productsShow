"""
认证文档模块
为API文档系统提供认证相关的配置和设置
"""
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object

class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """JWT认证方案扩展"""
    target_class = 'users.authentication.JWTAuthentication'
    name = 'JWTAuth'
    
    def get_security_definition(self, auto_schema):
        """获取安全定义"""
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix='Bearer',
            bearer_format='JWT',
        )
