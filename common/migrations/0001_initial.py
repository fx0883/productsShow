"""
初始迁移-创建租户模型
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='租户名称')),
                ('status', models.CharField(choices=[('active', '活跃'), ('suspended', '暂停'), ('deleted', '已删除')], default='active', max_length=20, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '租户',
                'verbose_name_plural': '租户',
                'db_table': 'tenants',
                'ordering': ['id'],
            },
        ),
    ]
