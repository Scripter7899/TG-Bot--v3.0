@echo off
echo ========================================
echo FULL-TG v3.0 - Quick Setup Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13.3 from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found
python --version

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [3/4] Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo Created .env file from template
    echo.
    echo IMPORTANT: Please edit .env file and add your Telegram API credentials
    echo Get them from: https://my.telegram.org
) else (
    echo .env file already exists
)

echo.
echo [4/4] Creating directories...
if not exist sessions mkdir sessions
if not exist logs mkdir logs
if not exist data mkdir data
if not exist data\exports mkdir data\exports
if not exist data\backups mkdir data\backups

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API_ID and API_HASH
echo 2. Run: python main.py
echo.
echo For help, check README.md
echo.
pause
