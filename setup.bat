@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AI Startup Competition Project Setup
echo ========================================

echo Checking Python installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.6 or newer.
    exit /b 1
)

:: Check for Visual C++ Build Tools (required for scikit-learn)
echo Checking for Visual C++ Build Tools...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Version >nul 2>&1
if %errorlevel% neq 0 (
    echo Visual C++ Build Tools not found. These are required for scikit-learn.
    echo Please install Visual C++ Build Tools 2015 or newer.
    echo You can download it from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    choice /C YN /M "Do you want to continue anyway?"
    if !errorlevel! equ 2 exit /b 1
)

:: Run the setup Python script
echo Running environment setup...
python setup_venv.py

:: Ask if user wants to run the application now
choice /C YN /M "Do you want to run the application now?"
if %errorlevel% equ 1 (
    call run.bat
)

echo Setup complete.
exit /b 0
