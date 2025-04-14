"""
工具函数模块
提供各种实用工具函数
"""
import uuid
import datetime
import json
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder


class CustomJSONEncoder(DjangoJSONEncoder):
    """
    扩展的JSON编码器，支持更多类型
    """
    def default(self, obj):
        # 处理UUID
        if isinstance(obj, uuid.UUID):
            return str(obj)
            
        # 处理时间类型
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
            
        # 处理集合类型
        if isinstance(obj, set):
            return list(obj)
            
        # 处理模型实例
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return obj.to_dict()
            
        # 调用父类方法
        return super().default(obj)


def to_json(data):
    """
    将数据转换为JSON字符串
    :param data: 要转换的数据
    :return: JSON字符串
    """
    return json.dumps(data, cls=CustomJSONEncoder)


def generate_token():
    """
    生成唯一令牌
    :return: 令牌字符串
    """
    return str(uuid.uuid4())


def get_client_ip(request):
    """
    获取客户端IP地址
    :param request: 请求对象
    :return: IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_timestamp():
    """
    获取当前时间戳（毫秒）
    :return: 时间戳
    """
    return int(timezone.now().timestamp() * 1000)
