@echo off
cd /d D:\ccwork\Resona-Desktop-Pet
echo Starting pip install...
venv\Scripts\pip install -r requirements.txt --verbose
echo EXIT CODE: %ERRORLEVEL%
echo DONE > install_complete.txt
