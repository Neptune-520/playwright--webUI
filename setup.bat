@echo off
chcp 65001 >nul
echo ========================================
echo Auto Test Platform - Setup Script
echo ========================================
echo.

echo [1/5] Checking Python environment...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

echo.
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo [3/5] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [4/5] Installing Playwright browsers...
playwright install chromium

echo.
echo [5/5] Initializing database...
python manage.py migrate
python manage.py init_sample_data

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo To start the server:
echo   1. Activate venv: venv\Scripts\activate
echo   2. Start Django: python manage.py runserver
echo   3. Visit: http://127.0.0.1:8000
echo.
echo For async tasks, start Celery:
echo   celery -A automation_test_platform worker -l info --pool=solo
echo.
pause
