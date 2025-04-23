@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Running application...
python run.py --all
exit /b 0
