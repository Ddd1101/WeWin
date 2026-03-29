import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建company表
print("\nCreating company table...")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS company (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        code TEXT NOT NULL UNIQUE,
        address TEXT DEFAULT '',
        contact_name TEXT DEFAULT '',
        contact_phone TEXT DEFAULT '',
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("Company table created successfully")
except Exception as e:
    print(f"Error creating company table: {e}")

# 插入默认公司记录
print("\nInserting default company record...")
try:
    # 检查是否已存在公司记录
    cursor.execute("SELECT id FROM company LIMIT 1;")
    result = cursor.fetchone()
    if not result:
        cursor.execute('''
        INSERT INTO company (name, code, is_active)
        VALUES ('默认企业', 'DEFAULT', 1)
        ''')
        print("Default company record inserted successfully")
    else:
        print("Company record already exists")
except Exception as e:
    print(f"Error inserting company record: {e}")

# 提交更改并关闭连接
conn.commit()
conn.close()

print("\nCompany table creation and initialization completed.")
