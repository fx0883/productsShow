# 变体产品数据库存储示例

本文档通过SQL语句和示例数据详细说明变体产品如何在数据库中存储，以CSV文件`vSimpleNew2.csv`中的变体产品为例。

## 1. 数据库表结构

首先，我们展示相关表的建表SQL语句：

### 1.1 产品表 (products)

```sql
CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) NOT NULL UNIQUE,
  sku VARCHAR(100) NOT NULL UNIQUE,
  type VARCHAR(20) NOT NULL DEFAULT 'simple',
  status VARCHAR(20) NOT NULL DEFAULT 'draft',
  featured BOOLEAN NOT NULL DEFAULT 0,
  catalog_visibility VARCHAR(20) NOT NULL DEFAULT 'visible',
  description TEXT,
  short_description TEXT,
  price DECIMAL(10, 2),
  regular_price DECIMAL(10, 2),
  sale_price DECIMAL(10, 2),
  sale_price_start_date DATETIME,
  sale_price_end_date DATETIME,
  stock_quantity INT NOT NULL DEFAULT 0,
  stock_status VARCHAR(20) NOT NULL DEFAULT 'instock',
  backorders_allowed BOOLEAN NOT NULL DEFAULT 0,
  sold_individually BOOLEAN NOT NULL DEFAULT 0,
  weight DECIMAL(10, 2),
  length DECIMAL(10, 2),
  width DECIMAL(10, 2),
  height DECIMAL(10, 2),
  shipping_class VARCHAR(100),
  reviews_allowed BOOLEAN NOT NULL DEFAULT 1,
  purchase_note TEXT,
  gtin VARCHAR(100),
  external_url VARCHAR(255),
  button_text VARCHAR(100),
  brand VARCHAR(100),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX (status, type),
  INDEX (name)
);
```

### 1.2 产品图片表 (product_images)

```sql
CREATE TABLE product_images (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  image VARCHAR(255),
  image_url VARCHAR(255),
  alt_text VARCHAR(255),
  is_featured BOOLEAN NOT NULL DEFAULT 0,
  `order` INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  INDEX (product_id, is_featured),
  INDEX (product_id, `order`)
);
```

### 1.3 属性表 (attributes)

```sql
CREATE TABLE attributes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  is_global BOOLEAN NOT NULL DEFAULT 0,
  INDEX (name)
);
```

### 1.4 属性值表 (attribute_values)

```sql
CREATE TABLE attribute_values (
  id INT AUTO_INCREMENT PRIMARY KEY,
  attribute_id INT NOT NULL,
  value VARCHAR(255) NOT NULL,
  slug VARCHAR(100) NOT NULL,
  description TEXT,
  FOREIGN KEY (attribute_id) REFERENCES attributes(id) ON DELETE CASCADE,
  UNIQUE KEY (attribute_id, value),
  INDEX (attribute_id, slug)
);
```

### 1.5 产品属性关联表 (product_attributes)

```sql
CREATE TABLE product_attributes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  attribute_id INT NOT NULL,
  is_visible BOOLEAN NOT NULL DEFAULT 1,
  is_variation BOOLEAN NOT NULL DEFAULT 0,
  position INT NOT NULL DEFAULT 0,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY (attribute_id) REFERENCES attributes(id) ON DELETE CASCADE,
  UNIQUE KEY (product_id, attribute_id),
  INDEX (product_id, is_variation)
);
```

### 1.6 产品属性值关联表 (product_attribute_values)

```sql
CREATE TABLE product_attribute_values (
  product_attribute_id INT NOT NULL,
  attribute_value_id INT NOT NULL,
  PRIMARY KEY (product_attribute_id, attribute_value_id),
  FOREIGN KEY (product_attribute_id) REFERENCES product_attributes(id) ON DELETE CASCADE,
  FOREIGN KEY (attribute_value_id) REFERENCES attribute_values(id) ON DELETE CASCADE
);
```

### 1.7 产品变体表 (product_variations)

```sql
CREATE TABLE product_variations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  name VARCHAR(255),
  sku VARCHAR(100),
  gtin VARCHAR(100),
  price DECIMAL(10, 2),
  regular_price DECIMAL(10, 2),
  sale_price DECIMAL(10, 2),
  sale_price_start_date DATETIME,
  sale_price_end_date DATETIME,
  tax_status VARCHAR(20) NOT NULL DEFAULT 'taxable',
  tax_class VARCHAR(100),
  weight DECIMAL(10, 2),
  length DECIMAL(10, 2),
  width DECIMAL(10, 2),
  height DECIMAL(10, 2),
  stock_quantity INT NOT NULL DEFAULT 0,
  stock_status VARCHAR(20) NOT NULL DEFAULT 'instock',
  backorders_allowed BOOLEAN NOT NULL DEFAULT 0,
  sold_individually BOOLEAN NOT NULL DEFAULT 0,
  is_published BOOLEAN NOT NULL DEFAULT 1,
  description TEXT,
  image_id INT,
  position INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY (image_id) REFERENCES product_images(id) ON DELETE SET NULL,
  INDEX (product_id, position),
  INDEX (sku)
);
```

### 1.8 变体属性关联表 (variation_attributes)

```sql
CREATE TABLE variation_attributes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  variation_id INT NOT NULL,
  attribute_id INT NOT NULL,
  value_id INT NOT NULL,
  FOREIGN KEY (variation_id) REFERENCES product_variations(id) ON DELETE CASCADE,
  FOREIGN KEY (attribute_id) REFERENCES attributes(id) ON DELETE CASCADE,
  FOREIGN KEY (value_id) REFERENCES attribute_values(id) ON DELETE CASCADE,
  UNIQUE KEY (variation_id, attribute_id),
  INDEX (variation_id, attribute_id, value_id)
);
```

## 2. 示例数据

以下是基于`vSimpleNew2.csv`文件中变体产品的示例数据，展示如何在数据库中存储。

### 2.1 主产品

```sql
INSERT INTO products (
  name, slug, sku, type, status, featured, catalog_visibility, 
  description, stock_status, reviews_allowed
) VALUES (
  'VL-EXCL-DT-056', 'vl-excl-dt-056', 'VL-EXCL-DT-056', 'variable', 
  'published', 0, 'visible', 'VL-EXCL-DT-056', 'instock', 1
);
-- 新插入记录的ID: 1
```

### 2.2 产品图片

```sql
-- 第一张图片（餐桌图片）
INSERT INTO product_images (
  product_id, image_url, is_featured, `order`
) VALUES (
  1, 'https://dev3.grandeurdesignz.com/wp-content/uploads/2025/03/main-55.png', 
  1, 0
);
-- 新插入记录的ID: 1

-- 第二张图片（椅子图片）
INSERT INTO product_images (
  product_id, image_url, is_featured, `order`
) VALUES (
  1, 'https://dev3.grandeurdesignz.com/wp-content/uploads/2025/03/001-3.png', 
  0, 1
);
-- 新插入记录的ID: 2
```

### 2.3 属性

```sql
-- 添加type属性
INSERT INTO attributes (
  name, slug, is_global
) VALUES (
  'type', 'type', 0
);
-- 新插入记录的ID: 1

-- 添加size属性
INSERT INTO attributes (
  name, slug, is_global
) VALUES (
  'size', 'size', 0
);
-- 新插入记录的ID: 2
```

### 2.4 属性值

```sql
-- 添加type属性值 - Long Dining Table
INSERT INTO attribute_values (
  attribute_id, value, slug
) VALUES (
  1, 'Long Dining Table', 'long-dining-table'
);
-- 新插入记录的ID: 1

-- 添加type属性值 - Dining Chair
INSERT INTO attribute_values (
  attribute_id, value, slug
) VALUES (
  1, 'Dining Chair', 'dining-chair'
);
-- 新插入记录的ID: 2

-- 添加size属性值 - 2200mm x 1080mm x 780mm
INSERT INTO attribute_values (
  attribute_id, value, slug
) VALUES (
  2, '2200mm x 1080mm x 780mm', '2200mm-x-1080mm-x-780mm'
);
-- 新插入记录的ID: 3

-- 添加size属性值 - 1800mm x 920mm x 800mm
INSERT INTO attribute_values (
  attribute_id, value, slug
) VALUES (
  2, '1800mm x 920mm x 800mm', '1800mm-x-920mm-x-800mm'
);
-- 新插入记录的ID: 4

-- 添加size属性值 - 520mm x 500mm x 1000mm
INSERT INTO attribute_values (
  attribute_id, value, slug
) VALUES (
  2, '520mm x 500mm x 1000mm', '520mm-x-500mm-x-1000mm'
);
-- 新插入记录的ID: 5
```

### 2.5 产品属性关联

```sql
-- 添加产品与type属性的关联
INSERT INTO product_attributes (
  product_id, attribute_id, is_visible, is_variation, position
) VALUES (
  1, 1, 1, 1, 0
);
-- 新插入记录的ID: 1

-- 添加产品与size属性的关联
INSERT INTO product_attributes (
  product_id, attribute_id, is_visible, is_variation, position
) VALUES (
  1, 2, 1, 1, 1
);
-- 新插入记录的ID: 2
```

### 2.6 产品属性值关联

```sql
-- 产品的type属性关联到"Long Dining Table"值
INSERT INTO product_attribute_values (
  product_attribute_id, attribute_value_id
) VALUES (
  1, 1
);

-- 产品的type属性关联到"Dining Chair"值
INSERT INTO product_attribute_values (
  product_attribute_id, attribute_value_id
) VALUES (
  1, 2
);

-- 产品的size属性关联到"2200mm x 1080mm x 780mm"值
INSERT INTO product_attribute_values (
  product_attribute_id, attribute_value_id
) VALUES (
  2, 3
);

-- 产品的size属性关联到"1800mm x 920mm x 800mm"值
INSERT INTO product_attribute_values (
  product_attribute_id, attribute_value_id
) VALUES (
  2, 4
);

-- 产品的size属性关联到"520mm x 500mm x 1000mm"值
INSERT INTO product_attribute_values (
  product_attribute_id, attribute_value_id
) VALUES (
  2, 5
);
```

### 2.7 产品变体

```sql
-- 添加第一个变体 - 2200mm餐桌
INSERT INTO product_variations (
  product_id, name, sku, regular_price, tax_status, 
  stock_status, is_published, image_id, position
) VALUES (
  1, 'VL-EXCL-DT-056 - Long Dining Table, 2200mm x 1080mm x 780mm', 
  '', 12300, 'taxable', 'instock', 1, 1, 1
);
-- 新插入记录的ID: 1

-- 添加第二个变体 - 1800mm餐桌
INSERT INTO product_variations (
  product_id, name, sku, regular_price, tax_status, 
  stock_status, is_published, image_id, position
) VALUES (
  1, 'VL-EXCL-DT-056 - Long Dining Table, 1800mm x 920mm x 800mm', 
  '', 10000, 'taxable', 'instock', 1, 1, 2
);
-- 新插入记录的ID: 2

-- 添加第三个变体 - 餐椅
INSERT INTO product_variations (
  product_id, name, sku, regular_price, tax_status, 
  stock_status, is_published, image_id, position
) VALUES (
  1, 'VL-EXCL-DT-056 - Dining Chair, 520mm x 500mm x 1000mm', 
  'P01#餐椅', 5000, 'taxable', 'instock', 1, 2, 3
);
-- 新插入记录的ID: 3
```

### 2.8 变体属性关联

```sql
-- 第一个变体(2200mm餐桌)的type属性为"Long Dining Table"
INSERT INTO variation_attributes (
  variation_id, attribute_id, value_id
) VALUES (
  1, 1, 1
);

-- 第一个变体(2200mm餐桌)的size属性为"2200mm x 1080mm x 780mm"
INSERT INTO variation_attributes (
  variation_id, attribute_id, value_id
) VALUES (
  1, 2, 3
);

-- 第二个变体(1800mm餐桌)的type属性为"Long Dining Table"
INSERT INTO variation_attributes (
  variation_id, attribute_id, value_id
) VALUES (
  2, 1, 1
);

-- 第二个变体(1800mm餐桌)的size属性为"1800mm x 920mm x 800mm"
INSERT INTO variation_attributes (
  variation_id, attribute_id, value_id
) VALUES (
  2, 2, 4
);

-- 第三个变体(餐椅)的type属性为"Dining Chair"
INSERT INTO variation_attributes (
  variation_id, attribute_id, value_id
) VALUES (
  3, 1, 2
);

-- 第三个变体(餐椅)的size属性为"520mm x 500mm x 1000mm"
INSERT INTO variation_attributes (
  variation_id, attribute_id, value_id
) VALUES (
  3, 2, 5
);
```

## 3. 数据查询示例

以下示例展示如何通过SQL查询获取变体产品的完整信息。

### 3.1 获取主产品及其所有变体

```sql
SELECT p.*, 
       COUNT(pv.id) as variation_count
FROM products p
LEFT JOIN product_variations pv ON p.id = pv.product_id
WHERE p.id = 1
GROUP BY p.id;
```

### 3.2 获取主产品的所有图片

```sql
SELECT * 
FROM product_images 
WHERE product_id = 1 
ORDER BY `order`;
```

### 3.3 获取主产品的所有属性及其可能值

```sql
SELECT pa.id as product_attribute_id, 
       a.id as attribute_id, 
       a.name as attribute_name, 
       a.is_global, 
       pa.is_visible, 
       pa.is_variation,
       GROUP_CONCAT(av.value SEPARATOR ', ') as attribute_values
FROM product_attributes pa
JOIN attributes a ON pa.attribute_id = a.id
JOIN product_attribute_values pav ON pa.id = pav.product_attribute_id
JOIN attribute_values av ON pav.attribute_value_id = av.id
WHERE pa.product_id = 1
GROUP BY pa.id
ORDER BY pa.position;
```

### 3.4 获取所有变体及其详细信息

```sql
SELECT pv.*, pi.image_url
FROM product_variations pv
LEFT JOIN product_images pi ON pv.image_id = pi.id
WHERE pv.product_id = 1
ORDER BY pv.position;
```

### 3.5 获取特定变体的所有属性

```sql
-- 这里以第3个变体(餐椅)为例
SELECT a.name as attribute_name, 
       av.value as attribute_value
FROM variation_attributes va
JOIN attributes a ON va.attribute_id = a.id
JOIN attribute_values av ON va.value_id = av.id
WHERE va.variation_id = 3;
```

### 3.6 查找匹配特定属性组合的变体

```sql
-- 查找type='Dining Chair'且size='520mm x 500mm x 1000mm'的变体
SELECT pv.*
FROM product_variations pv
JOIN variation_attributes va1 ON pv.id = va1.variation_id
JOIN variation_attributes va2 ON pv.id = va2.variation_id
JOIN attribute_values av1 ON va1.value_id = av1.id
JOIN attribute_values av2 ON va2.value_id = av2.id
JOIN attributes a1 ON va1.attribute_id = a1.id
JOIN attributes a2 ON va2.attribute_id = a2.id
WHERE pv.product_id = 1
  AND a1.name = 'type' AND av1.value = 'Dining Chair'
  AND a2.name = 'size' AND av2.value = '520mm x 500mm x 1000mm';
```

## 4. 数据库关系图

```
products (主产品)
  ↓ 1:n
product_images (产品图片)
  ↑ 1:n ↓ 1:n
product_variations (产品变体)
  ↓ 1:n
variation_attributes (变体属性值)
  ↓ n:1
attribute_values (属性值)
  ↑ n:1
attributes (属性)
  ↑ 1:n
product_attributes (产品属性)
  ↑ n:1 ↓ 1:n
product_attribute_values (产品属性值关联)
```

## 5. 注意事项

1. **数据一致性**：所有变体必须关联到同一个主产品，且每个变体必须指定所有用于变异的属性值。

2. **图片处理**：
   - 主产品可以有多张图片，通过`is_featured`字段标记主图
   - 每个变体可以关联到一张特定图片，通过`image_id`外键引用

3. **SKU管理**：
   - 主产品必须有唯一SKU
   - 变体可以有也可以没有SKU，如果有则应该唯一

4. **属性系统**：
   - 属性可以是全局的（用于所有产品）或特定于产品的
   - 属性可以用于生成变体（`is_variation=1`）或仅用于显示（`is_variation=0`）
   - 属性可以在前台显示（`is_visible=1`）或仅用于后台（`is_visible=0`）

5. **多语言支持**：
   - 产品名称、描述等可以通过翻译表支持多语言
   - 属性值也可以有多语言版本

## 6. 性能考虑

1. 为提高性能，已在相关字段上建立了索引，特别是外键和经常用于筛选的字段
2. 对于大型产品目录，考虑实施缓存策略
3. 变体数据查询可能涉及多表连接，应谨慎设计查询语句以优化性能
