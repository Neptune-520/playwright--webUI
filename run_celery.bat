@echo off
chcp 65001 >nul
echo Starting Celery Worker...
call venv\Scripts\activate.bat
celery -A automation_test_platform worker -l info --pool=solo
