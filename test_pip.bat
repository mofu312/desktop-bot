@echo on
cd /d D:\ccwork\Resona-Desktop-Pet
echo HELLO > test_out.txt
dir venv\Scripts\pip.exe >> test_out.txt
venv\Scripts\pip.exe --version >> test_out.txt 2>&1
echo DONE >> test_out.txt
