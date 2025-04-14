"""
JWT认证模块
提供JWT令牌的生成、验证和管理功能
"""
import jwt
from datetime import datetime, timedelta, timezone as dt_timezone
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from common.exceptions import TokenException, TokenExpiredException
from .models import User, UserToken


class JWTAuthentication(BaseAuthentication):
    """
    JWT认证类
    实现基于JWT令牌的用户认证
    """
    
    def authenticate(self, request):
        """
        验证请求中的JWT令牌
        :param request: 请求对象
        :return: (user, token) 元组或None
        """
        # 从请求头中获取令牌
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        # 提取令牌
        token = auth_header.split(' ')[1]
        if not token:
            return None
            
        try:
            # 查找令牌
            token_obj = UserToken.objects.filter(
                token=token,
                token_type='access',
                is_valid=True,
                expired_at__gt=timezone.now()
            ).select_related('user').first()
            
            if not token_obj:
                raise TokenException("无效的令牌或令牌已过期")
                
            # 解码令牌
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # 验证令牌用户和过期时间
            user_id = payload.get('user_id')
            if not user_id or int(user_id) != token_obj.user.id:
                raise TokenException("令牌用户信息不匹配")
                
            exp = payload.get('exp')
            if not exp or datetime.fromtimestamp(exp, tz=dt_timezone.utc) < timezone.now():
                # 如果令牌已过期，将其标记为无效
                token_obj.is_valid = False
                token_obj.save(update_fields=['is_valid'])
                raise TokenExpiredException()
                
            # 返回用户和令牌对象
            return (token_obj.user, token_obj)
            
        except jwt.PyJWTError as e:
            raise TokenException(f"令牌解析失败: {str(e)}")
        except TokenException as e:
            raise e
        except Exception as e:
            raise TokenException(f"认证失败: {str(e)}")
    
    def authenticate_header(self, request):
        """
        返回认证头部名称
        :param request: 请求对象
        :return: 认证头部名称
        """
        return 'Bearer'


class TokenManager:
    """
    令牌管理工具类
    用于生成和管理JWT令牌
    """
    
    @staticmethod
    def generate_tokens(user):
        """
        为用户生成访问令牌和刷新令牌
        :param user: 用户对象
        :return: (access_token, refresh_token, access_token_obj, refresh_token_obj) 元组
        """
        # 生成访问令牌
        access_token_expiry = timezone.now() + timedelta(hours=1)
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': int(access_token_expiry.timestamp()),
            'iat': int(timezone.now().timestamp()),
            'type': 'access'
        }
        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # 确保access_token是字符串类型
        if isinstance(access_token, bytes):
            access_token = access_token.decode('utf-8')
        
        # 生成刷新令牌
        refresh_token_expiry = timezone.now() + timedelta(days=7)
        refresh_payload = {
            'user_id': user.id,
            'exp': int(refresh_token_expiry.timestamp()),
            'iat': int(timezone.now().timestamp()),
            'type': 'refresh'
        }
        refresh_token = jwt.encode(
            refresh_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # 确保refresh_token是字符串类型
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode('utf-8')
        
        # 保存令牌到数据库
        # 先使当前用户的同类型令牌失效
        UserToken.objects.filter(
            user=user,
            token_type='access',
            is_valid=True
        ).update(is_valid=False)
        
        UserToken.objects.filter(
            user=user,
            token_type='refresh',
            is_valid=True
        ).update(is_valid=False)
        
        # 创建新的令牌记录
        access_token_obj = UserToken.objects.create(
            user=user,
            token=access_token,
            token_type='access',
            expired_at=access_token_expiry
        )
        
        refresh_token_obj = UserToken.objects.create(
            user=user,
            token=refresh_token,
            token_type='refresh',
            expired_at=refresh_token_expiry
        )
        
        return (access_token, refresh_token, access_token_obj, refresh_token_obj)
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """
        使用刷新令牌生成新的访问令牌
        :param refresh_token: 刷新令牌
        :return: (access_token, access_token_obj) 元组
        """
        try:
            # 验证刷新令牌
            token_obj = UserToken.objects.filter(
                token=refresh_token,
                token_type='refresh',
                is_valid=True,
                expired_at__gt=timezone.now()
            ).select_related('user').first()
            
            if not token_obj:
                raise TokenException("无效的刷新令牌")
                
            # 解码令牌
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # 验证令牌类型和用户
            if payload.get('type') != 'refresh':
                raise TokenException("无效的令牌类型")
                
            user_id = payload.get('user_id')
            if not user_id or int(user_id) != token_obj.user.id:
                raise TokenException("令牌用户信息不匹配")
                
            # 生成新的访问令牌
            user = token_obj.user
            
            # 使当前用户的访问令牌失效
            UserToken.objects.filter(
                user=user,
                token_type='access',
                is_valid=True
            ).update(is_valid=False)
            
            # 生成新的访问令牌
            access_token_expiry = timezone.now() + timedelta(hours=1)
            access_payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': int(access_token_expiry.timestamp()),
                'iat': int(timezone.now().timestamp()),
                'type': 'access'
            }
            access_token = jwt.encode(
                access_payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            
            # 确保access_token是字符串类型
            if isinstance(access_token, bytes):
                access_token = access_token.decode('utf-8')
            
            # 保存新令牌到数据库
            access_token_obj = UserToken.objects.create(
                user=user,
                token=access_token,
                token_type='access',
                expired_at=access_token_expiry
            )
            
            return (access_token, access_token_obj)
            
        except jwt.PyJWTError as e:
            raise TokenException(f"令牌解析失败: {str(e)}")
        except TokenException as e:
            raise e
        except Exception as e:
            raise TokenException(f"刷新令牌失败: {str(e)}")

    @staticmethod
    def verify_token(token, is_refresh=False):
        """
        验证令牌
        :param token: 令牌字符串
        :param is_refresh: 是否是刷新令牌
        :return: (user, payload, token_obj) 元组
        """
        try:
            # 确保token是字符串类型
            if isinstance(token, bytes):
                token = token.decode('utf-8')
                
            # 解码令牌
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # 验证令牌类型
            token_type = 'refresh' if is_refresh else 'access'
            if payload.get('type') != token_type:
                raise TokenException("无效的令牌类型")
            
            # 验证令牌是否存在于数据库且有效
            token_obj = UserToken.objects.filter(
                token=token,
                token_type=token_type,
                is_valid=True,
                expired_at__gt=timezone.now()
            ).select_related('user').first()
            
            if not token_obj:
                raise TokenException("无效的令牌或令牌已过期")
            
            user_id = payload.get('user_id')
            if not user_id or int(user_id) != token_obj.user.id:
                raise TokenException("令牌用户信息不匹配")
            
            # 返回用户和令牌信息
            return (token_obj.user, payload, token_obj)
        
        except jwt.PyJWTError as e:
            raise TokenException(f"令牌解析失败: {str(e)}")
        except TokenException as e:
            raise e
        except Exception as e:
            raise TokenException(f"验证令牌失败: {str(e)}")

    @staticmethod
    def invalidate_token(token, token_type='access'):
        """
        使令牌失效
        :param token: 令牌字符串
        :param token_type: 令牌类型
        :return: 是否成功使令牌失效
        """
        # 查找并使令牌失效
        token_obj = UserToken.objects.filter(
            token=token,
            token_type=token_type,
            is_valid=True
        ).first()
        
        if token_obj:
            token_obj.is_valid = False
            token_obj.save(update_fields=['is_valid'])
            return True
            
        return False
    
    @staticmethod
    def invalidate_user_tokens(user, token_type=None):
        """
        使用户的所有令牌失效
        :param user: 用户对象
        :param token_type: 令牌类型，None表示所有类型
        :return: 失效的令牌数量
        """
        query = UserToken.objects.filter(user=user, is_valid=True)
        if token_type:
            query = query.filter(token_type=token_type)
            
        count = query.count()
        query.update(is_valid=False)
        
        return count
