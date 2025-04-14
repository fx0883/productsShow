# Generated by Django 5.2 on 2025-04-10 10:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('exports', '0001_initial'),
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='exporthistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='export_history', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exportlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='export_lists', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exporthistory',
            name='export_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='exports.exportlist'),
        ),
        migrations.AddField(
            model_name='exportlistitem',
            name='export_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='exports.exportlist'),
        ),
        migrations.AddField(
            model_name='exportlistitem',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
        migrations.AddField(
            model_name='exportlistitem',
            name='variation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.productvariation'),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='export_templates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exporthistory',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='exports.exporttemplate'),
        ),
        migrations.AddConstraint(
            model_name='exportlistitem',
            constraint=models.CheckConstraint(condition=models.Q(('product__isnull', False), ('variation__isnull', False), _connector='OR'), name='either_product_or_variation'),
        ),
    ]
