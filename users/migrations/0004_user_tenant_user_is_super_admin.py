"""
添加租户外键和超级管理员标志到User模型
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),  # 依赖common应用的初始迁移
        ('users', '0003_user_avatar_user_nick_name'),   # 依赖先前的用户迁移
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tenant',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='users',
                to='common.tenant',
                verbose_name='租户',
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='is_super_admin',
            field=models.BooleanField(default=False, verbose_name='超级管理员'),
        ),
    ]
