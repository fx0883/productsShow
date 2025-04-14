"""
自定义异常模块
定义系统中使用的各种业务异常
"""
from rest_framework.exceptions import APIException
from rest_framework import status
from .response import ResponseCode


class BusinessException(APIException):
    """
    业务逻辑异常基类
    用法：raise BusinessException(code=10001, message="自定义错误消息")
    """
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, code=ResponseCode.BUSINESS_ERROR, message="业务处理异常", data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(detail=message)


class AuthenticationException(BusinessException):
    """认证相关异常"""
    status_code = status.HTTP_401_UNAUTHORIZED
    
    def __init__(self, code=ResponseCode.UNAUTHORIZED, message="认证失败", data=None):
        super().__init__(code=code, message=message, data=data)


class PermissionException(BusinessException):
    """权限相关异常"""
    status_code = status.HTTP_403_FORBIDDEN
    
    def __init__(self, code=ResponseCode.PERMISSION_DENIED, message="权限不足", data=None):
        super().__init__(code=code, message=message, data=data)


class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""
    status_code = status.HTTP_404_NOT_FOUND
    
    def __init__(self, code=ResponseCode.RESOURCE_NOT_FOUND, message="资源不存在", data=None):
        super().__init__(code=code, message=message, data=data)


class ValidationException(BusinessException):
    """数据验证异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, code=ResponseCode.PARAM_ERROR, message="数据验证失败", data=None):
        super().__init__(code=code, message=message, data=data)


class TokenException(AuthenticationException):
    """令牌相关异常"""
    
    def __init__(self, message="无效的令牌", code=ResponseCode.TOKEN_INVALID, data=None):
        super().__init__(code=code, message=message, data=data)


class TokenExpiredException(TokenException):
    """令牌过期异常"""
    
    def __init__(self, message="令牌已过期", data=None):
        super().__init__(message=message, code=ResponseCode.TOKEN_EXPIRED, data=data)
