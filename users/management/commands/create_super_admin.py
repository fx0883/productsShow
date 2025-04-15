from django.core.management.base import BaseCommand
from users.models import User
from common.models import Tenant
from django.db import transaction


class Command(BaseCommand):
    help = '创建一个拥有超级管理员权限的用户'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='用户名', required=True)
        parser.add_argument('--password', type=str, help='密码', required=True)
        parser.add_argument('--email', type=str, help='电子邮箱', required=True)
        parser.add_argument('--nick_name', type=str, help='昵称', default=None)
        parser.add_argument('--phone', type=str, help='手机号码', default=None)
        parser.add_argument('--tenant', type=str, help='关联租户名称（如果不指定则使用默认租户）', default=None)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        nick_name = options.get('nick_name') or username
        phone = options.get('phone')
        tenant_name = options.get('tenant')

        try:
            with transaction.atomic():
                # 检查用户是否已存在
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.ERROR(f'用户名 "{username}" 已存在！'))
                    return
                
                if User.objects.filter(email=email).exists():
                    self.stdout.write(self.style.ERROR(f'邮箱 "{email}" 已被注册！'))
                    return
                
                # 获取或创建关联租户
                if tenant_name:
                    tenant, created = Tenant.objects.get_or_create(
                        name=tenant_name, 
                        defaults={'status': 'active'}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'已创建租户 "{tenant_name}"'))
                else:
                    # 查找或创建默认租户
                    tenant, created = Tenant.objects.get_or_create(
                        name='默认租户', 
                        defaults={'status': 'active'}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS('已创建默认租户'))
                
                # 创建超级管理员用户
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    nick_name=nick_name,
                    phone=phone,
                    tenant=tenant,
                    is_admin=True,
                    is_super_admin=True,
                    is_member=True,
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f'已成功创建超级管理员用户：{username}，关联租户：{tenant.name}'
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建超级管理员失败: {str(e)}'))
