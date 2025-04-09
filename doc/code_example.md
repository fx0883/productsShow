# 代码高亮示例

本文档用于测试不同编程语言的代码高亮效果。

## Python 代码示例

```python
def hello_world():
    """打印Hello World并返回值"""
    print("Hello, World!")
    return 42

# 这是一个注释
class Person:
    def __init__(self, name, age):
        self.name = name  # 姓名
        self.age = age    # 年龄
        
    def greet(self):
        return f"你好，我是{self.name}，今年{self.age}岁。"

# 创建一个实例并调用方法
person = Person("张三", 30)
message = person.greet()
print(message)
```

## JavaScript 代码示例

```javascript
// 定义一个函数
function calculateSum(a, b) {
    // 这是一个注释
    console.log('计算两数之和');
    return a + b;
}

// 定义一个类
class Product {
    constructor(name, price) {
        this.name = name;
        this.price = price;
    }
    
    getInfo() {
        return `商品名称：${this.name}，价格：${this.price}元`;
    }
}

// 创建实例
const phone = new Product('智能手机', 4999);
console.log(phone.getInfo());
```

## HTML 代码示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>示例页面</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
        }
        h1 {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>欢迎访问</h1>
        <p>这是一个示例页面。</p>
        <button id="btn">点击我</button>
    </div>
    
    <script>
        document.getElementById('btn').addEventListener('click', function() {
            alert('按钮被点击了！');
        });
    </script>
</body>
</html>
```

## CSS 代码示例

```css
/* 主样式 */
body {
    font-family: 'Microsoft YaHei', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
    margin: 0;
    padding: 20px;
}

/* 头部样式 */
header {
    background: #35424a;
    color: white;
    padding: 20px;
    text-align: center;
}

/* 导航栏 */
nav {
    background: #333;
    color: #fff;
}

nav ul {
    padding: 0;
    list-style: none;
}

nav li {
    display: inline;
    margin-right: 20px;
}

nav a {
    color: white;
    text-decoration: none;
}

/* 响应式设计 */
@media(max-width: 768px) {
    header {
        padding: 10px;
    }
    
    nav li {
        display: block;
        margin: 10px 0;
    }
}
```

## SQL 代码示例

```sql
-- 创建用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建商品表
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 查询示例
SELECT p.name, p.price, c.name AS category
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE p.price > 100
ORDER BY p.price DESC
LIMIT 10;
```

## JSON 示例

```json
{
    "id": 123,
    "name": "智能手机",
    "price": 4999.00,
    "inStock": true,
    "specs": {
        "screen": "6.7英寸",
        "processor": "骁龙8 Gen 2",
        "ram": "12GB",
        "storage": "512GB"
    },
    "colors": ["黑色", "白色", "蓝色"],
    "reviews": [
        {
            "user": "user123",
            "rating": 5,
            "comment": "非常好用的手机！"
        },
        {
            "user": "user456",
            "rating": 4,
            "comment": "性价比很高，但电池续航一般。"
        }
    ]
}
```
