cd Server
.\venv\Scripts\Activate.ps1
python manage.py runserver

# 部署

# 进入Server目录

cd Server

# 创建虚拟环境（推荐）

python3 -m venv venv

# 激活虚拟环境

source venv/bin/activate

# 安装依赖

pip install -r requirements.txt

# 1. 数据库迁移（Django 默认 SQLite，无需额外配置）

python3 manage.py makemigrations # 生成迁移文件（有模型时执行）
python3 manage.py migrate # 执行迁移，创建数据库

# 2. 创建超级用户（可选，访问后台管理）

python3 manage.py createsuperuser

# 按提示输入用户名、邮箱、密码（如：admin / admin@test.com / 123456）

# 使用 gunicorn

pip install gunicorn
gunicorn wewin.wsgi:application -b 0.0.0.0:8000

# 前端部署

cd ~/workplace_shop/WeWin/Page

# 安装依赖

npm install

# 构建生产版本

npm run build

# 使用 serve 运行（简单方式）

npm install -g serve
serve -s dist -l 5173
