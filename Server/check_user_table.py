import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查user表
print("\nChecking user table...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
result = cursor.fetchone()
if result:
    print("User table exists")
    # 显示表结构
    cursor.execute("PRAGMA table_info(user);")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
else:
    print("User table does not exist")

# 关闭连接
conn.close()
