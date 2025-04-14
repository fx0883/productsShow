from django.contrib import admin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import (
    Category, Tag, Product, ProductImage, 
    Attribute, AttributeValue, ProductAttribute, 
    ProductVariation, VariationAttribute
)

# 产品图片内联
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'image_url', 'alt_text', 'is_featured', 'order')

# 产品属性内联
class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ('attribute', 'used_for_variations')

# 产品变体内联
class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = ('sku', 'name', 'price', 'stock_quantity', 'stock_status', 'is_default')

# 变体属性内联
class VariationAttributeInline(admin.TabularInline):
    model = VariationAttribute
    extra = 1
    fields = ('attribute', 'value')

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title', 'slug', 'parent')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    fieldsets = (
        (None, {'fields': ('name', 'short_name', 'slug', 'parent', 'description', 'image')}),
    )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'type', 'status', 'price', 'stock_quantity', 'created_at')
    list_filter = ('type', 'status', 'featured', 'catalog_visibility', 'created_at')
    search_fields = ('name', 'sku', 'vl_id', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    filter_horizontal = ('categories', 'tags', 'upsell_products', 'cross_sell_products')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, ProductAttributeInline, ProductVariationInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'slug', 'sku', 'vl_id', 'type', 'status', 'featured')
        }),
        ('分类与标签', {
            'fields': ('categories', 'tags')
        }),
        ('描述', {
            'fields': ('description', 'short_description')
        }),
        ('价格', {
            'fields': ('price', 'regular_price', 'sale_price', 'sale_price_start_date', 'sale_price_end_date')
        }),
        ('库存', {
            'fields': ('stock_quantity', 'stock_status', 'backorders_allowed', 'sold_individually')
        }),
        ('尺寸重量', {
            'fields': ('weight', 'length', 'width', 'height', 'shipping_class'),
            'classes': ('collapse',)
        }),
        ('其他设置', {
            'fields': ('catalog_visibility', 'reviews_allowed', 'purchase_note', 'gtin', 'brand'),
            'classes': ('collapse',)
        }),
        ('相关产品', {
            'fields': ('upsell_products', 'cross_sell_products'),
            'classes': ('collapse',)
        }),
        ('外部产品', {
            'fields': ('external_url', 'button_text'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'is_featured', 'order', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('product__name', 'product__sku', 'alt_text')
    raw_id_fields = ('product',)
    readonly_fields = ('created_at',)

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'has_predefined_values', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('name', 'attribute', 'slug', 'sort_order')
    list_filter = ('attribute',)
    search_fields = ('name', 'slug', 'attribute__name')
    raw_id_fields = ('attribute',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'price', 'stock_quantity', 'stock_status', 'is_default')
    list_filter = ('stock_status', 'is_default', 'created_at')
    search_fields = ('sku', 'vl_id', 'name', 'product__name', 'product__sku')
    raw_id_fields = ('product', 'image')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [VariationAttributeInline]
    fieldsets = (
        ('基本信息', {
            'fields': ('product', 'sku', 'vl_id', 'name', 'description', 'is_default', 'sort_order')
        }),
        ('价格', {
            'fields': ('price', 'regular_price', 'sale_price', 'sale_price_start_date', 'sale_price_end_date')
        }),
        ('库存', {
            'fields': ('stock_quantity', 'stock_status')
        }),
        ('尺寸重量', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('图片', {
            'fields': ('image',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
