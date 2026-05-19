import sqlite3
import os
import hashlib

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建user表
print("\nCreating user table...")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        password TEXT NOT NULL,
        last_login DATETIME NULL,
        is_superuser BOOLEAN NOT NULL DEFAULT 0,
        username TEXT NOT NULL UNIQUE,
        first_name TEXT NOT NULL DEFAULT '',
        last_name TEXT NOT NULL DEFAULT '',
        email TEXT NOT NULL DEFAULT '',
        is_staff BOOLEAN NOT NULL DEFAULT 0,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        uid TEXT NULL UNIQUE,
        user_type TEXT NOT NULL DEFAULT 'temporary',
        company_id INTEGER NULL,
        created_by_id INTEGER NULL,
        phone TEXT NULL,
        real_name TEXT NULL,
        FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE,
        FOREIGN KEY (created_by_id) REFERENCES user(id) ON DELETE SET NULL
    )
    ''')
    print("User table created successfully")
except Exception as e:
    print(f"Error creating user table: {e}")

# 插入默认超级管理员用户
print("\nInserting default super admin user...")
try:
    # 检查是否已存在用户记录
    cursor.execute("SELECT id FROM user LIMIT 1;")
    result = cursor.fetchone()
    if not result:
        # 生成密码哈希（简单示例，实际应该使用Django的密码哈希）
        password = 'admin123'
        # 这里使用简单的MD5哈希，实际应该使用Django的make_password函数
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        cursor.execute('''
        INSERT INTO user (
            username, password, is_superuser, is_staff, is_active,
            user_type, company_id, created_by_id, real_name
        ) VALUES (
            'admin', ?, 1, 1, 1, 'super_admin', 1, NULL, '超级管理员'
        )
        ''', (password_hash,))
        print("Default super admin user inserted successfully")
    else:
        print("User record already exists")
except Exception as e:
    print(f"Error inserting user record: {e}")

# 提交更改并关闭连接
conn.commit()
conn.close()

print("\nUser table creation and initialization completed.")
