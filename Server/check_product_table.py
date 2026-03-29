import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查product表
print("\nChecking product table...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product';")
result = cursor.fetchone()
if result:
    print("Product table exists")
    # 显示表结构
    cursor.execute("PRAGMA table_info(product);")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 检查是否包含code列
    has_code = False
    for col in columns:
        if col[1] == 'code':
            has_code = True
            break
    if has_code:
        print("Product table has code column")
    else:
        print("Product table does NOT have code column")
else:
    print("Product table does not exist")

# 关闭连接
conn.close()
