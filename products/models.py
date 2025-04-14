from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from users.models import User

class Category(MPTTModel):
    """
    产品分类，支持多级分类
    使用Django-MPTT实现树形结构
    """
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'
        
    class MPTTMeta:
        order_insertion_by = ['name']
        
    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    产品标签
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = '标签'
        verbose_name_plural = '标签'
        
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    产品基本信息
    """
    TYPE_CHOICES = (
        ('simple', '简单产品'),
        ('variable', '变体产品'),
        ('grouped', '组合产品'),
        ('external', '外部/affiliate产品'),
    )
    
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
        ('trash', '回收站'),
    )
    
    VISIBILITY_CHOICES = (
        ('visible', '可见'),
        ('catalog', '仅在目录中可见'),
        ('search', '仅在搜索中可见'),
        ('hidden', '隐藏'),
    )
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    sku = models.CharField(max_length=100, unique=True)
    vl_id = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='simple')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    catalog_visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='visible')
    description = models.TextField(blank=True)
    short_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price_start_date = models.DateTimeField(null=True, blank=True)
    sale_price_end_date = models.DateTimeField(null=True, blank=True)
    menu_order = models.IntegerField(default=0, help_text="WooCommerce产品排序字段，值越小排序越靠前")
    categories = models.ManyToManyField(Category, related_name='products')
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    stock_quantity = models.IntegerField(default=0)
    stock_status = models.CharField(max_length=20, default='instock')
    backorders_allowed = models.BooleanField(default=False)
    sold_individually = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_class = models.CharField(max_length=100, blank=True)
    reviews_allowed = models.BooleanField(default=True)
    purchase_note = models.TextField(blank=True)
    gtin = models.CharField(max_length=100, blank=True, help_text="GTIN, UPC, EAN, or ISBN")
    upsell_products = models.ManyToManyField('self', blank=True, related_name='upsell_to', symmetrical=False)
    cross_sell_products = models.ManyToManyField('self', blank=True, related_name='cross_sell_to', symmetrical=False)
    external_url = models.URLField(blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = '产品'
        verbose_name_plural = '产品'
        ordering = ['menu_order', '-created_at']
        
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """
    产品图片
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    image_url = models.URLField(blank=True, help_text="外部图片URL，用于导入数据")
    alt_text = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        verbose_name = '产品图片'
        verbose_name_plural = '产品图片'
        ordering = ['order']
        
    def __str__(self):
        return f"Image for {self.product.name} ({self.id})"


class Attribute(models.Model):
    """
    产品属性定义，例如"颜色"、"尺寸"等
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    has_predefined_values = models.BooleanField(default=True, help_text="是否有预定义的可选值")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attributes'
        verbose_name = '属性'
        verbose_name_plural = '属性'
        
    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """
    属性的可选值，例如颜色属性的"红色"、"蓝色"等
    """
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'attribute_values'
        verbose_name = '属性值'
        verbose_name_plural = '属性值'
        unique_together = ('attribute', 'slug')
        ordering = ['sort_order']
        
    def __str__(self):
        return f"{self.attribute.name}: {self.name}"


class ProductAttribute(models.Model):
    """
    产品与属性的关联，定义产品的哪些属性可用于变体
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    used_for_variations = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_attributes'
        verbose_name = '产品属性'
        verbose_name_plural = '产品属性'
        unique_together = ('product', 'attribute')
        
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}"


class ProductVariation(models.Model):
    """
    产品变体，例如不同颜色、尺寸的同款产品
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    sku = models.CharField(max_length=100, unique=True)
    vl_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price_start_date = models.DateTimeField(null=True, blank=True)
    sale_price_end_date = models.DateTimeField(null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    stock_status = models.CharField(max_length=20, default='instock')
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='variations')
    is_default = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_variations'
        verbose_name = '产品变体'
        verbose_name_plural = '产品变体'
        ordering = ['sort_order']
        
    def __str__(self):
        return f"{self.product.name} - {self.name or self.sku}"


class VariationAttribute(models.Model):
    """
    变体与属性值的关联
    """
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'variation_attributes'
        verbose_name = '变体属性'
        verbose_name_plural = '变体属性'
        unique_together = ('variation', 'attribute')
        
    def __str__(self):
        return f"{self.variation.sku} - {self.attribute.name}: {self.value.name}"
