@echo off
REM Git Commit and Push Script for WeWin Project
REM Run this script after installing Git

echo ========================================
echo WeWin Project - Git Commit and Push
echo ========================================
echo.

REM Check if Git is installed
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Git is not installed or not in PATH.
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

REM Navigate to project directory
cd /d "%~dp0"

echo [1/5] Checking Git status...
git status

echo.
echo [2/5] Adding all changes to staging area...
git add .

echo.
echo [3/5] Committing changes...
git commit -m "docs: 整理项目文档并添加文档目录结构分析报告

- 添加项目结构分析报告
- 将所有文档文件整理到 document 目录
- 更新 .gitignore 忽略 JPG/JPEG 图片文件"

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Commit failed. Please check the errors above.
    pause
    exit /b 1
)

echo.
echo [4/5] Checking remote repository...
git remote -v

echo.
echo [5/5] Pushing to remote repository...
git push

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Push failed. Please check if:
    echo   1. You have push permissions
    echo   2. Your remote repository URL is correct
    echo   3. You have authentication configured
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! All changes have been committed and pushed.
echo ========================================
echo.
pause
