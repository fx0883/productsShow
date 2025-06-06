# Generated by Django 5.2 on 2025-04-10 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertoken',
            name='is_valid',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='usertoken',
            name='token_type',
            field=models.CharField(choices=[('access', '访问令牌'), ('refresh', '刷新令牌')], default='access', max_length=20),
        ),
        migrations.AddIndex(
            model_name='usertoken',
            index=models.Index(fields=['token'], name='user_tokens_token_f22396_idx'),
        ),
        migrations.AddIndex(
            model_name='usertoken',
            index=models.Index(fields=['user', 'token_type'], name='user_tokens_user_id_f56e54_idx'),
        ),
    ]
