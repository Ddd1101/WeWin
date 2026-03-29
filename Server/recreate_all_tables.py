import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 删除所有相关表（按依赖顺序）
tables = ['finishedproductaccessory', 'finishedproductbead', 'finishedproduct', 'accessory', 'bead', 'product']

print("\nDropping tables...")
for table in tables:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        print(f"Dropped table: {table}")
    except Exception as e:
        print(f"Error dropping table {table}: {e}")

# 创建product表
print("\nCreating product table...")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        product_type TEXT NOT NULL,
        cost_price DECIMAL(10,2) NOT NULL,
        selling_price DECIMAL(10,2) NOT NULL,
        location TEXT DEFAULT '',
        supplier TEXT DEFAULT '',
        company_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_by_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("Product table created successfully")
except Exception as e:
    print(f"Error creating product table: {e}")

# 创建bead表
print("\nCreating bead table...")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bead (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER UNIQUE,
        material TEXT DEFAULT '',
        size TEXT DEFAULT '',
        color TEXT DEFAULT '',
        FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
    )
    ''')
    print("Bead table created successfully")
except Exception as e:
    print(f"Error creating bead table: {e}")

# 创建accessory表
print("\nCreating accessory table...")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accessory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER UNIQUE,
        material TEXT DEFAULT '',
        size TEXT DEFAULT '',
        color TEXT DEFAULT '',
        FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
    )
    ''')
    print("Accessory table created successfully")
except Exception as e:
    print(f"Error creating accessory table: {e}")

# 创建finished_product表
print("\nCreating finished_product table...")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS finished_product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER UNIQUE,
        FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
    )
    ''')
    print("FinishedProduct table created successfully")
except Exception as e:
    print(f"Error creating finished_product table: {e}")

# 创建finished_product_bead表
print("\nCreating finished_product_bead table...")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS finished_product_bead (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finished_product_id INTEGER,
        bead_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (finished_product_id) REFERENCES finished_product(id) ON DELETE CASCADE,
        FOREIGN KEY (bead_id) REFERENCES bead(id) ON DELETE CASCADE
    )
    ''')
    print("FinishedProductBead table created successfully")
except Exception as e:
    print(f"Error creating finished_product_bead table: {e}")

# 创建finished_product_accessory表
print("\nCreating finished_product_accessory table...")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS finished_product_accessory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finished_product_id INTEGER,
        accessory_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (finished_product_id) REFERENCES finished_product(id) ON DELETE CASCADE,
        FOREIGN KEY (accessory_id) REFERENCES accessory(id) ON DELETE CASCADE
    )
    ''')
    print("FinishedProductAccessory table created successfully")
except Exception as e:
    print(f"Error creating finished_product_accessory table: {e}")

# 提交更改并关闭连接
conn.commit()
conn.close()

print("\nAll tables recreated successfully.")
