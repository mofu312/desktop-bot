@echo off
cd /d D:\ccwork\Resona-Desktop-Pet
echo Creating venv...
python -m venv venv --clear
echo Installing requirements...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt
echo DONE > install_complete.txt
