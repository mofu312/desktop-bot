@echo off
cd /d D:\ccwork\Resona-Desktop-Pet
venv\Scripts\pip.exe install -r requirements.txt
echo EXIT_CODE=%ERRORLEVEL%
echo COMPLETE > install_done.txt
