from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
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
    readonly_fields = ('get_image_preview',)

    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image_url)
        return "无图片"
    get_image_preview.short_description = "图片预览"

# 产品属性内联
class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ('attribute', 'used_for_variations')

# 产品变体内联
class ProductVariationInline(admin.StackedInline):
    model = ProductVariation
    extra = 0
    fields = ('sku', 'name', 'price', 'regular_price', 'sale_price', 'stock_quantity', 'stock_status', 'is_default', 'image')
    raw_id_fields = ('image',)
    show_change_link = True

# 变体属性内联
class VariationAttributeInline(admin.TabularInline):
    model = VariationAttribute
    extra = 1
    fields = ('attribute', 'value')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "value" and request.GET.get('attribute'):
            attribute_id = request.GET.get('attribute')
            kwargs["queryset"] = AttributeValue.objects.filter(attribute_id=attribute_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title', 'slug', 'parent', 'get_product_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug', 'description')
    list_filter = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'short_name', 'slug', 'parent', 'description', 'image')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_product_count(self, obj):
        return obj.products.count()
    get_product_count.short_description = '产品数量'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_product_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_product_count(self, obj):
        return obj.products.count()
    get_product_count.short_description = '产品数量'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'get_categories', 'type', 'status', 'price', 'stock_status', 'get_images_count', 'get_variations_count', 'featured', 'created_at')
    list_filter = ('type', 'status', 'featured', 'catalog_visibility', 'stock_status', 'categories', 'tags', 'created_at', 'updated_at')
    search_fields = ('name', 'sku', 'vl_id', 'short_description', 'description', 'categories__name', 'tags__name')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    filter_horizontal = ('categories', 'tags', 'upsell_products', 'cross_sell_products')
    readonly_fields = ('created_at', 'updated_at', 'get_primary_image')
    inlines = [ProductImageInline, ProductAttributeInline, ProductVariationInline]
    list_per_page = 50
    actions = ['make_published', 'make_draft', 'mark_as_featured', 'unmark_as_featured']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'slug', 'sku', 'vl_id', 'type', 'status', 'featured', 'get_primary_image')
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
            'fields': ('catalog_visibility', 'reviews_allowed', 'purchase_note', 'gtin', 'brand', 'menu_order'),
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

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()[:3]])
    get_categories.short_description = '分类'

    def get_images_count(self, obj):
        return obj.images.count()
    get_images_count.short_description = '图片数'

    def get_variations_count(self, obj):
        return obj.variations.count()
    get_variations_count.short_description = '变体数'

    def get_primary_image(self, obj):
        featured_image = obj.images.filter(is_featured=True).first()
        if not featured_image:
            featured_image = obj.images.first()
        if featured_image and featured_image.image:
            return format_html('<img src="{}" style="max-height: 150px; max-width: 300px;" />', featured_image.image.url)
        return "无图片"
    get_primary_image.short_description = "主图"

    def make_published(self, request, queryset):
        queryset.update(status='published')
    make_published.short_description = "将所选产品标记为已发布"

    def make_draft(self, request, queryset):
        queryset.update(status='draft')
    make_draft.short_description = "将所选产品标记为草稿"

    def mark_as_featured(self, request, queryset):
        queryset.update(featured=True)
    mark_as_featured.short_description = "将所选产品标记为精选"

    def unmark_as_featured(self, request, queryset):
        queryset.update(featured=False)
    unmark_as_featured.short_description = "取消所选产品的精选标记"

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'get_image_preview', 'alt_text', 'is_featured', 'order', 'created_at')
    list_filter = ('is_featured', 'created_at', 'updated_at')
    search_fields = ('product__name', 'product__sku', 'alt_text')
    raw_id_fields = ('product',)
    readonly_fields = ('created_at', 'updated_at', 'get_image_preview')
    list_editable = ('is_featured', 'order')

    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image_url)
        return "无图片"
    get_image_preview.short_description = "图片预览"

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'has_predefined_values', 'get_values_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('has_predefined_values', 'created_at')

    def get_values_count(self, obj):
        return obj.values.count()
    get_values_count.short_description = '值数量'

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('name', 'attribute', 'slug', 'sort_order')
    list_filter = ('attribute', 'created_at')
    search_fields = ('name', 'slug', 'attribute__name', 'description')
    raw_id_fields = ('attribute',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('sort_order',)

@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'name', 'price', 'stock_quantity', 'stock_status', 'is_default', 'get_attributes_display')
    list_filter = ('stock_status', 'is_default', 'created_at', 'updated_at')
    search_fields = ('sku', 'vl_id', 'name', 'product__name', 'product__sku', 'description')
    raw_id_fields = ('product', 'image')
    readonly_fields = ('created_at', 'updated_at', 'get_attributes_display')
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
    
    def get_attributes_display(self, obj):
        attrs = obj.attributes.all()
        if not attrs:
            return "无属性"
        return ", ".join([f"{attr.attribute.name}: {attr.value.name}" for attr in attrs])
    get_attributes_display.short_description = "属性"

@admin.register(VariationAttribute)
class VariationAttributeAdmin(admin.ModelAdmin):
    list_display = ('variation', 'attribute', 'value')
    list_filter = ('attribute', 'created_at')
    search_fields = ('variation__sku', 'attribute__name', 'value__name')
    raw_id_fields = ('variation',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """根据选择的attribute动态过滤value的选项"""
        if db_field.name == "value" and request.resolver_match.kwargs.get('object_id'):
            variation_attr = VariationAttribute.objects.get(id=request.resolver_match.kwargs.get('object_id'))
            kwargs["queryset"] = AttributeValue.objects.filter(attribute=variation_attr.attribute)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
