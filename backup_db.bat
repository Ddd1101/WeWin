@echo off
rem WeWin 数据库一键备份
rem 用法：backup_db.bat [--keep N]
cd /d "%~dp0Server"
call venv\Scripts\python.exe backup_db.py %*
