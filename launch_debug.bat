@echo off
cd /d "D:\ccwork\Resona-Desktop-Pet"
echo [Resona] Launching debug mode...
echo Stderr will be saved to crash_debug.log
"venv\Scripts\python.exe" main.py 2>crash_debug.log
echo App exited with code: %errorlevel%
echo ===== STDERR LOG =====
type crash_debug.log
echo ===== END =====
pause
