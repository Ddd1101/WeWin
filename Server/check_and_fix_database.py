import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查所有表
tables = ['product', 'bead', 'accessory', 'finishedproduct', 'finishedproductbead', 'finishedproductaccessory']

print("\nExisting tables:")
for table in tables:
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
    result = cursor.fetchone()
    if result:
        print(f"- {table}")
        # 显示表结构
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        print(f"  Columns:")
        for col in columns:
            print(f"    {col[1]} ({col[2]})")
    else:
        print(f"- {table} (DOES NOT EXIST)")

# 创建缺失的表
print("\nCreating missing tables...")

# 检查product表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product';")
if not cursor.fetchone():
    print("Creating product table...")
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
    print("Product table created")
else:
    print("Product table already exists")

# 创建bead表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bead';")
if not cursor.fetchone():
    print("Creating bead table...")
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
    print("Bead table created")
else:
    print("Bead table already exists")

# 创建accessory表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accessory';")
if not cursor.fetchone():
    print("Creating accessory table...")
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
    print("Accessory table created")
else:
    print("Accessory table already exists")

# 创建finishedproduct表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finishedproduct';")
if not cursor.fetchone():
    print("Creating finishedproduct table...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS finishedproduct (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER UNIQUE,
        FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
    )
    ''')
    print("FinishedProduct table created")
else:
    print("FinishedProduct table already exists")

# 创建finishedproductbead表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finishedproductbead';")
if not cursor.fetchone():
    print("Creating finishedproductbead table...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS finishedproductbead (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finished_product_id INTEGER,
        bead_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (finished_product_id) REFERENCES finishedproduct(id) ON DELETE CASCADE,
        FOREIGN KEY (bead_id) REFERENCES bead(id) ON DELETE CASCADE
    )
    ''')
    print("FinishedProductBead table created")
else:
    print("FinishedProductBead table already exists")

# 创建finishedproductaccessory表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finishedproductaccessory';")
if not cursor.fetchone():
    print("Creating finishedproductaccessory table...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS finishedproductaccessory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finished_product_id INTEGER,
        accessory_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (finished_product_id) REFERENCES finishedproduct(id) ON DELETE CASCADE,
        FOREIGN KEY (accessory_id) REFERENCES accessory(id) ON DELETE CASCADE
    )
    ''')
    print("FinishedProductAccessory table created")
else:
    print("FinishedProductAccessory table already exists")

# 提交更改并关闭连接
conn.commit()
conn.close()

print("\nDatabase check and fix completed.")
