@echo off
cd /d d:\workplace_shop\WeWin\Server
call venv\Scripts\activate.bat
python manage.py runserver 127.0.0.1:8003
