import sqlite3
import os

# 获取数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, 'db.sqlite3')

print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查现有表
print("\nExisting tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# 检查product表结构
print("\nProduct table schema:")
try:
    cursor.execute("PRAGMA table_info(product);")
    columns = cursor.fetchall()
    for column in columns:
        print(f"- {column[1]}: {column[2]}")
except sqlite3.OperationalError as e:
    print(f"Product table does not exist: {e}")

# 检查bead表
print("\nBead table:")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bead';")
    if cursor.fetchone():
        print("Bead table exists")
    else:
        print("Bead table does not exist")
except Exception as e:
    print(f"Error checking bead table: {e}")

# 检查accessory表
print("\nAccessory table:")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accessory';")
    if cursor.fetchone():
        print("Accessory table exists")
    else:
        print("Accessory table does not exist")
except Exception as e:
    print(f"Error checking accessory table: {e}")

# 检查finished_product表
print("\nFinishedProduct table:")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finished_product';")
    if cursor.fetchone():
        print("FinishedProduct table exists")
    else:
        print("FinishedProduct table does not exist")
except Exception as e:
    print(f"Error checking finished_product table: {e}")

# 检查finished_product_bead表
print("\nFinishedProductBead table:")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finished_product_bead';")
    if cursor.fetchone():
        print("FinishedProductBead table exists")
    else:
        print("FinishedProductBead table does not exist")
except Exception as e:
    print(f"Error checking finished_product_bead table: {e}")

# 检查finished_product_accessory表
print("\nFinishedProductAccessory table:")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finished_product_accessory';")
    if cursor.fetchone():
        print("FinishedProductAccessory table exists")
    else:
        print("FinishedProductAccessory table does not exist")
except Exception as e:
    print(f"Error checking finished_product_accessory table: {e}")

# 关闭连接
conn.close()
print("\nCheck completed.")
