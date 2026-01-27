@echo off
setlocal
cd /d %~dp0

:: 1. Check local runtime
if exist "runtime\python.exe" (
    set "PYTHON_EXEC=runtime\python.exe"
    goto START
)

:: 2. Check virtual environment
if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXEC=venv\Scripts\python.exe"
    goto START
)

:: 3. Check system python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXEC=python"
    goto START
)

echo [ERROR] No valid Python environment found! Please run setup.ps1 first.
pause
exit /b

:START
echo [Resona] Using environment: %PYTHON_EXEC%
%PYTHON_EXEC% main.py
if %errorlevel% neq 0 (
    echo [Resona] Program exited with error code: %errorlevel%
    pause
)
endlocal
