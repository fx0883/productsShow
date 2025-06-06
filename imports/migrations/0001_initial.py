# Generated by Django 5.2 on 2025-04-10 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImportHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_path', models.CharField(max_length=255)),
                ('format', models.CharField(choices=[('woocommerce', 'WooCommerce'), ('custom', '自定义')], default='woocommerce', max_length=20)),
                ('status', models.CharField(choices=[('pending', '待处理'), ('processing', '处理中'), ('completed', '已完成'), ('failed', '失败')], default='pending', max_length=20)),
                ('total_rows', models.IntegerField(default=0)),
                ('processed_rows', models.IntegerField(default=0)),
                ('success_rows', models.IntegerField(default=0)),
                ('error_rows', models.IntegerField(default=0)),
                ('product_count', models.IntegerField(default=0)),
                ('variation_count', models.IntegerField(default=0)),
                ('error_log', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '导入历史',
                'verbose_name_plural': '导入历史',
                'db_table': 'import_history',
            },
        ),
        migrations.CreateModel(
            name='ImportMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('source_format', models.CharField(default='woocommerce', max_length=50)),
                ('field_mapping', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '导入映射',
                'verbose_name_plural': '导入映射',
                'db_table': 'import_mappings',
            },
        ),
    ]
