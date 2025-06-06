"""
用户序列化器模块
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, UserToken


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'password', 'password_confirm', 'nick_name', 'avatar')
        extra_kwargs = {
            'email': {'required': True},
            'nick_name': {'required': False},
            'avatar': {'required': False}
        }
    
    def validate(self, attrs):
        # 验证两次密码是否一致
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        
        # 验证邮箱是否已存在
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "该邮箱已被注册"})
        
        return attrs
    
    def create(self, validated_data):
        # 移除非模型字段
        validated_data.pop('password_confirm')
        
        # 创建用户
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data.get('phone', ''),
            nick_name=validated_data.get('nick_name', ''),
            avatar=validated_data.get('avatar', None)
        )
        
        # 设置密码
        user.set_password(validated_data['password'])
        user.save()
        
        # 创建用户配置
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        
        # 至少提供用户名或邮箱之一
        if not username and not email:
            raise serializers.ValidationError("请提供用户名或邮箱")
        
        # 查找用户
        if email:
            user = authenticate(
                self.context['request'],
                username=User.objects.filter(email=email).first().username if User.objects.filter(email=email).exists() else '',
                password=password
            )
        else:
            user = authenticate(
                self.context['request'],
                username=username,
                password=password
            )
        
        # 验证结果
        if not user:
            raise serializers.ValidationError("用户名或密码错误")
        
        if not user.is_active:
            raise serializers.ValidationError("用户已被禁用")
        
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'is_admin', 'is_member', 'date_joined', 'last_login', 'nick_name', 'avatar')
        read_only_fields = ('id', 'date_joined', 'last_login')


class UserProfileSerializer(serializers.ModelSerializer):
    """用户配置序列化器"""
    class Meta:
        model = UserProfile
        fields = ('preferred_language', 'date_format')


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详细信息序列化器"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'is_admin', 'is_member', 
                 'date_joined', 'last_login', 'profile', 'first_name', 'last_name', 'nick_name', 'avatar')
        read_only_fields = ('id', 'date_joined', 'last_login')


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        # 验证两次新密码是否一致
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "两次密码不一致"})
        
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """令牌刷新序列化器"""
    refresh_token = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """密码重置序列化器"""
    user_id = serializers.IntegerField(required=True)
    super_key = serializers.CharField(required=True, write_only=True)


class UserTenantAssignSerializer(serializers.Serializer):
    """用户租户分配序列化器"""
    user_id = serializers.IntegerField(required=True)
    tenant_id = serializers.IntegerField(required=True)
    
    def validate_user_id(self, value):
        """验证用户ID"""
        from users.models import User
        
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("用户不存在")
        return value
    
    def validate_tenant_id(self, value):
        """验证租户ID"""
        from common.models import Tenant
        
        try:
            Tenant.objects.get(id=value)
        except Tenant.DoesNotExist:
            raise serializers.ValidationError("租户不存在")
        return value


class TenantUserCreateSerializer(serializers.ModelSerializer):
    """租户内用户创建序列化器"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone', 'nick_name', 'is_admin', 'is_member']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }
        
    def validate(self, attrs):
        """
        验证密码匹配和唯一性约束
        """
        # 验证密码是否匹配
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "两次密码输入不一致"})
            
        # 验证用户名唯一性
        username = attrs.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "该用户名已存在"})
            
        # 验证邮箱唯一性
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "该邮箱已被注册"})
        
        # 删除password_confirm字段
        if 'password_confirm' in attrs:
            del attrs['password_confirm']
            
        return attrs
