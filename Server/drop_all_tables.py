import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\nDropping all tables...")
for table in tables:
    table_name = table[0]
    # 跳过系统表
    if table_name.startswith('sqlite_'):
        continue
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"Dropped table: {table_name}")
    except Exception as e:
        print(f"Error dropping table {table_name}: {e}")

# 提交更改并关闭连接
conn.commit()
conn.close()

print("\nAll tables dropped successfully.")
