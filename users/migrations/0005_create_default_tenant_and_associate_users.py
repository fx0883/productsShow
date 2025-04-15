"""
创建默认租户并关联现有用户
"""
from django.db import migrations


def create_default_tenant_and_associate_users(apps, schema_editor):
    """
    创建默认租户（ID=1）并将所有现有用户关联到这个租户
    """
    # 获取模型引用
    Tenant = apps.get_model('common', 'Tenant')
    User = apps.get_model('users', 'User')

    # 创建默认租户（如果不存在）
    default_tenant, created = Tenant.objects.get_or_create(
        id=1,
        defaults={
            'name': '默认租户',
            'status': 'active',
        }
    )

    # 将所有没有关联租户的用户关联到默认租户
    User.objects.filter(tenant__isnull=True).update(tenant=default_tenant)

    # 设置管理员用户为超级管理员
    User.objects.filter(is_admin=True).update(is_super_admin=True)


def revert_default_tenant_and_user_association(apps, schema_editor):
    """
    撤销操作：取消用户与租户的关联，并删除默认租户
    """
    User = apps.get_model('users', 'User')
    Tenant = apps.get_model('common', 'Tenant')

    # 取消所有用户与默认租户的关联
    User.objects.filter(tenant__id=1).update(tenant=None)
    User.objects.update(is_super_admin=False)

    # 删除默认租户
    Tenant.objects.filter(id=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
        ('users', '0004_user_tenant_user_is_super_admin'),
    ]

    operations = [
        migrations.RunPython(
            create_default_tenant_and_associate_users,
            revert_default_tenant_and_user_association
        ),
    ]
