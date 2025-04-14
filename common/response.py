"""
API响应处理模块
提供统一的API响应格式和便捷的响应生成函数
"""
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import traceback
import sys


class APIResponse(Response):
    """
    自定义API响应类，统一API返回格式
    {
        "success": true/false,
        "code": 200,
        "message": "success",
        "data": {...},
        "meta": {...}
    }
    """
    def __init__(self, data=None, code=None, message="", 
                 success=None, status=None, headers=None, 
                 meta=None, exception=False, exception_obj=None, **kwargs):
        """初始化响应对象"""
        
        # 如果未指定code，则使用status
        if code is None:
            code = status or 200
            
        # 如果未指定success，则根据code判断
        if success is None:
            success = 200 <= code < 300
        
        # 构建meta数据    
        meta_data = meta or {
            "timestamp": timezone.now().isoformat()
        }
        
        # 添加异常信息
        if exception or exception_obj:
            if exception_obj:
                exc_type = exception_obj.__class__.__name__
                meta_data["exception"] = exc_type
                meta_data["exception_detail"] = str(exception_obj)
                # 在控制台打印详细的异常信息以便调试
                print(f"Exception in API response: {exc_type}: {exception_obj}")
                traceback.print_exc()
            else:
                meta_data["exception"] = "Unknown"
            
        # 构建标准响应结构
        std_data = {
            "success": success,
            "code": code,
            "message": message or self._get_default_message(code),
            "data": data,
            "meta": meta_data
        }
        
        # 调用父类构造函数
        super().__init__(data=std_data, status=status or code, 
                         headers=headers, exception=exception, **kwargs)
    
    def _get_default_message(self, code):
        """根据状态码获取默认消息"""
        messages = {
            200: "成功",
            201: "创建成功",
            204: "删除成功",
            400: "请求错误",
            401: "未授权",
            403: "禁止访问",
            404: "资源不存在",
            500: "服务器内部错误"
        }
        return messages.get(code, "未知状态")


def success_response(data=None, message=None, **kwargs):
    """
    成功响应工厂函数
    :param data: 响应数据
    :param message: 响应消息
    :return: APIResponse
    """
    return APIResponse(
        data=data,
        message=message or "成功",
        status=kwargs.pop('status_code', status.HTTP_200_OK),
        **kwargs
    )


def error_response(message=None, code=None, data=None, **kwargs):
    """
    错误响应工厂函数
    :param message: 错误消息
    :param code: 错误码
    :param data: 错误数据
    :return: APIResponse
    """
    # 获取异常对象（如果存在）
    exception_obj = kwargs.pop('exception_obj', None)
    # 如果是系统异常，默认使用500状态码
    status_code = kwargs.pop('status_code', status.HTTP_500_INTERNAL_SERVER_ERROR if exception_obj else status.HTTP_400_BAD_REQUEST)
    
    return APIResponse(
        success=False,
        message=message or "请求失败",
        code=code or status_code,
        data=data,
        status=status_code,
        exception=True,
        exception_obj=exception_obj,
        **kwargs
    )


# 常用响应状态码
class ResponseCode:
    """常用响应状态码"""
    # 成功系列: 2xx
    SUCCESS = 200
    CREATED = 201
    DELETED = 204
    
    # 客户端错误系列: 4xx
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    
    # 服务器错误系列: 5xx
    SERVER_ERROR = 500
    
    # 业务错误系列: 1xxxx
    SYSTEM_ERROR = 10000
    PARAM_ERROR = 10001
    
    # 认证错误系列: 2xxxx
    LOGIN_REQUIRED = 20000
    LOGIN_ERROR = 20001
    TOKEN_EXPIRED = 20002
    TOKEN_INVALID = 20003
    
    # 权限错误系列: 3xxxx
    PERMISSION_DENIED = 30000
    
    # 资源错误系列: 4xxxx
    RESOURCE_NOT_FOUND = 40000
    RESOURCE_CONFLICT = 40001
    
    # 业务逻辑错误系列: 5xxxx
    BUSINESS_ERROR = 50000
