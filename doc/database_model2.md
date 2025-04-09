# 商品管理系统 - 数据库模型设计

## 1. 数据库概述

商品管理系统采用MySQL数据库，使用Django ORM进行数据访问。数据模型设计遵循以下原则：

- 符合关系型数据库范式
- 适配WooCommerce产品数据结构
- 支持多语言内容
- 优化查询性能
- 维护数据完整性

## 2. 实体关系图

![实体关系图](https://placeholder-for-erd-diagram.com)

## 3. 核心数据模型

### 3.1 用户模型

#### User（用户）

```python
class User(AbstractUser):
    """
    扩展Django内置用户模型
    """
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_member = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
```

#### UserProfile（用户配置）

```python
class UserProfile(models.Model):
    """
    用户额外信息
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_language = models.CharField(max_length=10, default='zh-cn')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'
```

#### UserToken（用户令牌）

```python
class UserToken(models.Model):
    """
    用户JWT令牌管理
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255)
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_tokens'
        verbose_name = '用户令牌'
        verbose_name_plural = '用户令牌'
```

### 3.2 产品模型

#### Category（产品分类）

```python
class Category(MPTTModel):
    """
    产品分类，支持多级分类
    使用Django-MPTT实现树形结构
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
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
```

#### Product（产品）

```python
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
    categories = models.ManyToManyField(Category, related_name='products')
    tags = models.ManyToManyField('Tag', related_name='products', blank=True)
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
        ordering = ['-created_at']
```

#### ProductImage（产品图片）

```python
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
```

#### Attribute（属性）

```python
class Attribute(models.Model):
    """
    产品属性
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_global = models.BooleanField(default=False, help_text="全局属性可在所有产品中使用")
    
    class Meta:
        db_table = 'attributes'
        verbose_name = '属性'
        verbose_name_plural = '属性'
```

#### AttributeValue（属性值）

```python
class AttributeValue(models.Model):
    """
    属性值
    """
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'attribute_values'
        verbose_name = '属性值'
        verbose_name_plural = '属性值'
        unique_together = ('attribute', 'value')
```

#### ProductAttribute（产品属性关联）

```python
class ProductAttribute(models.Model):
    """
    产品与属性的关联
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    values = models.ManyToManyField(AttributeValue, related_name='products')
    is_visible = models.BooleanField(default=True, help_text="属性是否在产品页面可见")
    is_variation = models.BooleanField(default=False, help_text="是否用于创建变体")
    position = models.IntegerField(default=0, help_text="排序位置")
    
    class Meta:
        db_table = 'product_attributes'
        verbose_name = '产品属性'
        verbose_name_plural = '产品属性'
        unique_together = ('product', 'attribute')
```

#### ProductVariation（产品变体）

```python
class ProductVariation(models.Model):
    """
    产品变体
    """
    TAX_STATUS_CHOICES = (
        ('taxable', '应税'),
        ('shipping', '仅运费应税'),
        ('none', '不应税'),
    )
    
    STOCK_STATUS_CHOICES = (
        ('instock', '有货'),
        ('outofstock', '缺货'),
        ('onbackorder', '可接受缺货订单'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    name = models.CharField(max_length=255, blank=True, help_text="变体名称，通常自动生成")
    sku = models.CharField(max_length=100, blank=True)
    gtin = models.CharField(max_length=100, blank=True, help_text="GTIN, UPC, EAN, or ISBN")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price_start_date = models.DateTimeField(null=True, blank=True)
    sale_price_end_date = models.DateTimeField(null=True, blank=True)
    tax_status = models.CharField(max_length=20, choices=TAX_STATUS_CHOICES, default='taxable')
    tax_class = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='instock')
    backorders_allowed = models.BooleanField(default=False)
    sold_individually = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='variations')
    position = models.IntegerField(default=0, help_text="变体显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_variations'
        verbose_name = '产品变体'
        verbose_name_plural = '产品变体'
        ordering = ['position', 'id']
```

#### VariationAttribute（变体属性关联）

```python
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
```

#### Tag（标签）

```python
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
```

### 3.3 导出相关模型

#### ExportList（导出清单）

```python
class ExportList(models.Model):
    """
    用户导出清单
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_lists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'export_lists'
        verbose_name = '导出清单'
        verbose_name_plural = '导出清单'
```

#### ExportListItem（导出清单项）

```python
class ExportListItem(models.Model):
    """
    导出清单项
    """
    export_list = models.ForeignKey(ExportList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'export_list_items'
        verbose_name = '导出清单项'
        verbose_name_plural = '导出清单项'
        constraints = [
            models.CheckConstraint(
                check=models.Q(product__isnull=False) | models.Q(variation__isnull=False),
                name="either_product_or_variation"
            )
        ]
```

#### ExportTemplate（导出模板）

```python
class ExportTemplate(models.Model):
    """
    CSV导出模板
    """
    FORMAT_CHOICES = (
        ('woocommerce', 'WooCommerce'),
        ('custom', '自定义'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='woocommerce')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_templates')
    is_public = models.BooleanField(default=False)
    fields = models.JSONField(default=dict, help_text="要导出的字段配置")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'export_templates'
        verbose_name = '导出模板'
        verbose_name_plural = '导出模板'
```

#### ExportHistory（导出历史）

```python
class ExportHistory(models.Model):
    """
    导出历史记录
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_history')
    export_list = models.ForeignKey(ExportList, on_delete=models.CASCADE, null=True, blank=True)
    template = models.ForeignKey(ExportTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    product_count = models.IntegerField(default=0)
    variation_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'export_history'
        verbose_name = '导出历史'
        verbose_name_plural = '导出历史'
```

### 3.4 导入相关模型

#### ImportHistory（导入历史）

```python
class ImportHistory(models.Model):
    """
    导入历史记录
    """
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    )
    
    FORMAT_CHOICES = (
        ('woocommerce', 'WooCommerce'),
        ('custom', '自定义'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_history')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='woocommerce')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    success_rows = models.IntegerField(default=0)
    error_rows = models.IntegerField(default=0)
    product_count = models.IntegerField(default=0)
    variation_count = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'import_history'
        verbose_name = '导入历史'
        verbose_name_plural = '导入历史'
```

#### ImportMapping（导入映射）

```python
class ImportMapping(models.Model):
    """
    CSV导入字段映射
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_mappings')
    is_public = models.BooleanField(default=False)
    source_format = models.CharField(max_length=50, default='woocommerce')
    field_mapping = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'import_mappings'
        verbose_name = '导入映射'
        verbose_name_plural = '导入映射'
```

## 4. 数据库索引设计

为确保系统性能，对关键字段建立适当的索引：

### 4.1 产品相关索引

- `products.sku`：唯一索引，加速SKU查询
- `products.name`：普通索引，加速按名称搜索
- `products.status, products.type`：联合索引，加速状态和类型筛选
- `product_variations.sku`：索引，加速变体SKU查询
- `product_variations.product_id`：索引，加速获取产品的所有变体

### 4.2 属性相关索引

- `attributes.name`：索引，加速属性搜索
- `attribute_values.attribute_id, attribute_values.value`：联合索引，加速特定属性的值查询
- `variation_attributes.variation_id, variation_attributes.attribute_id`：联合索引，加速获取变体的特定属性

### 4.3 导出相关索引

- `export_list_items.export_list_id`：索引，加速获取清单内容
- `export_list_items.product_id`：索引，加速检查产品是否在清单中
- `export_history.user_id, export_history.created_at`：联合索引，加速获取用户的导出历史

## 5. 数据库迁移计划

数据库迁移将通过Django的迁移机制实现，分阶段进行：

1. **基础结构迁移**：创建核心表和关系
2. **属性系统迁移**：创建属性和变体相关表
3. **导出/导入系统迁移**：创建导出和导入相关表
4. **索引和约束迁移**：添加所有索引和约束

## 6. WooCommerce数据兼容性

系统设计考虑了与WooCommerce数据结构的兼容性：

### 6.1 产品数据字段匹配

| WooCommerce字段 | 系统数据模型 |
|----------------|-------------|
| Type | Product.type |
| SKU | Product.sku / ProductVariation.sku |
| Name | Product.name / ProductVariation.name |
| Published | Product.status |
| Is featured? | Product.featured |
| Visibility in catalog | Product.catalog_visibility |
| Description | Product.description |
| Short description | Product.short_description |
| Sale price | Product.sale_price / ProductVariation.sale_price |
| Regular price | Product.regular_price / ProductVariation.regular_price |
| Categories | Product.categories (多对多) |
| Tags | Product.tags (多对多) |
| Shipping class | Product.shipping_class |
| Images | ProductImage (一对多) |
| Parent | ProductVariation.product (外键) |
| Attribute name | Attribute.name |
| Attribute value(s) | AttributeValue.value |
| Attribute visible | ProductAttribute.is_visible |
| Attribute global | Attribute.is_global |

### 6.2 CSV导入导出支持

系统设计支持标准WooCommerce CSV格式的导入导出：

- **CSV表头映射**：系统字段与WooCommerce CSV表头自动映射
- **变体产品处理**：支持父-子关系的产品变体导入导出
- **属性处理**：支持全局属性和产品特定属性的导入导出
- **图片处理**：支持通过URL添加产品图片

## 7. 数据一致性和约束

为保证数据一致性，实施以下约束：

1. 每个变体必须关联到一个主产品
2. 导出清单项必须关联到产品或变体中的一个
3. 产品SKU在整个系统中唯一
4. 属性名称在整个系统中唯一
5. 属性值在同一属性内唯一
