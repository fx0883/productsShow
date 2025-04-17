from django.contrib import admin
from .models import ExportList, ExportListItem, ExportTemplate, ExportHistory
from django import forms

try:
    from django_json_widget.widgets import JSONEditorWidget
    HAS_JSON_WIDGET = True
except ImportError:
    HAS_JSON_WIDGET = False

class ExportListItemInline(admin.TabularInline):
    model = ExportListItem
    extra = 1
    fields = ('product', 'variation')
    raw_id_fields = ('product', 'variation')

@admin.register(ExportList)
class ExportListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ExportListItemInline]
    fieldsets = (
        (None, {'fields': ('user', 'name', 'description')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

@admin.register(ExportListItem)
class ExportListItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'export_list', 'product', 'variation', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('export_list__name', 'product__name', 'product__sku', 'variation__sku')
    raw_id_fields = ('export_list', 'product', 'variation')
    readonly_fields = ('added_at',)

class ExportTemplateForm(forms.ModelForm):
    class Meta:
        model = ExportTemplate
        fields = '__all__'
        if HAS_JSON_WIDGET:
            widgets = {
                'fields': JSONEditorWidget
            }

@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    form = ExportTemplateForm
    list_display = ('name', 'format', 'user', 'is_public', 'created_at', 'updated_at')
    list_filter = ('format', 'is_public', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'name', 'description')}),
        ('格式设置', {'fields': ('format', 'is_public', 'fields')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

@admin.register(ExportHistory)
class ExportHistoryAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'user', 'export_list', 'template', 'product_count', 'variation_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('file_name', 'user__username', 'export_list__name')
    raw_id_fields = ('user', 'export_list', 'template')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'export_list', 'template')}),
        ('文件信息', {'fields': ('file_name', 'file_path')}),
        ('数据统计', {'fields': ('product_count', 'variation_count')}),
        ('时间信息', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
