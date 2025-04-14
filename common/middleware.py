"""
中间件模块
用于处理请求/响应周期中的全局逻辑
"""
import json
import traceback
import logging
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status
from .exceptions import BusinessException
from .response import APIResponse, ResponseCode

# 配置日志
logger = logging.getLogger('django')


def custom_exception_handler(exc, context):
    """
    全局REST framework异常处理函数
    :param exc: 异常
    :param context: 上下文
    :return: APIResponse
    """
    if isinstance(exc, BusinessException):
        # 处理自定义业务异常
        return APIResponse(
            success=False,
            code=exc.code,
            message=exc.message,
            data=exc.data,
            status=exc.status_code
        )
    
    if isinstance(exc, ValidationError):
        # 处理验证错误，提取详细信息
        return APIResponse(
            success=False,
            code=ResponseCode.PARAM_ERROR,
            message="参数验证错误",
            data=exc.detail,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, APIException):
        # 处理DRF标准异常
        return APIResponse(
            success=False,
            code=exc.status_code,
            message=str(exc.detail),
            status=exc.status_code
        )
    
    # 处理其他未知异常
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return APIResponse(
        success=False,
        code=ResponseCode.SERVER_ERROR,
        message="服务器内部错误",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        meta={
            "timestamp": timezone.now().isoformat(),
            "exception": exc.__class__.__name__
        }
    )


class APIResponseMiddleware:
    """
    API响应中间件
    用于将Django标准响应转换为API标准响应格式
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 处理请求前的逻辑
        
        # 获取响应
        response = self.get_response(request)
        
        # 处理请求后的逻辑
        # 只处理API路径的响应
        if not self._should_process(request):
            return response
        
        # 如果是已处理过的APIResponse，直接返回
        if hasattr(response, '_apiresponse_formatted'):
            return response
            
        # 尝试格式化响应
        try:
            return self._format_response(response)
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            logger.error(traceback.format_exc())
            # 返回原始响应，避免中间件错误
            return response
    
    def _should_process(self, request):
        """
        判断是否需要处理该请求
        :param request: 请求对象
        :return: bool
        """
        # 只处理API路径的请求
        # 可根据需要自定义处理条件，如路径前缀、内容类型等
        return request.path.startswith('/api/')
    
    def _format_response(self, response):
        """
        格式化响应
        :param response: 原始响应对象
        :return: 格式化后的响应
        """
        # 如果已经是JSONResponse，尝试提取数据并重新格式化
        if isinstance(response, JsonResponse):
            try:
                # 提取数据
                content = response.content
                data = json.loads(content)
                
                # 检查是否已经符合格式
                if isinstance(data, dict) and 'success' in data and 'code' in data and 'message' in data:
                    return response
                
                # 创建新的标准响应
                std_response = APIResponse(
                    data=data,
                    code=response.status_code,
                    success=200 <= response.status_code < 300,
                    status=response.status_code
                )
                
                # 标记为已处理
                std_response._apiresponse_formatted = True
                
                # 复制原始响应的headers
                for header, value in response.items():
                    if header != 'Content-Type':  # 保留我们的Content-Type
                        std_response[header] = value
                
                return std_response
            except:
                # 解析失败则返回原始响应
                return response
        
        # 其他类型的响应暂不处理
        return response
