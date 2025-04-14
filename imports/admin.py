from django.contrib import admin
from .models import ImportHistory, ImportMapping

@admin.register(ImportHistory)
class ImportHistoryAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'user', 'format', 'status', 'total_rows', 'success_rows', 
                   'error_rows', 'product_count', 'variation_count', 'created_at')
    list_filter = ('status', 'format', 'created_at')
    search_fields = ('file_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'file_name', 'file_path')}),
        ('导入格式', {'fields': ('format',)}),
        ('状态信息', {'fields': ('status', 'total_rows', 'processed_rows', 'success_rows', 'error_rows', 
                            'product_count', 'variation_count')}),
        ('错误日志', {'fields': ('error_log',), 'classes': ('collapse',)}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

@admin.register(ImportMapping)
class ImportMappingAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_format', 'user', 'is_public', 'created_at', 'updated_at')
    list_filter = ('source_format', 'is_public', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'name', 'description')}),
        ('映射设置', {'fields': ('source_format', 'is_public', 'field_mapping')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
