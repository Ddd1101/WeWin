import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 删除所有相关表
tables = ['finishedproductaccessory', 'finishedproductbead', 'finishedproduct', 'accessory', 'bead', 'product']

print("\nDropping tables...")
for table in tables:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        print(f"Dropped table: {table}")
    except Exception as e:
        print(f"Error dropping table {table}: {e}")

# 提交更改并关闭连接
conn.commit()
conn.close()

print("\nAll tables dropped successfully.")
