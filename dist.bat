@echo off
setlocal
REM Tested with Python: 3.9.7, PyInstaller: 4.5.1

set VERSION=%1
set ZIP="C:\Program Files\WinRAR\WinRar.exe"
set DIST=dist
set D=ewlaunch-%VERSION%
set TGT=%D%.zip

pyinstaller --onefile --windowed ewlaunch_win.py --icon=ewlaunch.ico
pyinstaller --onefile ewlaunch.py

cd %DIST%
del /q %TGT% 2>nul
rmdir /q /s %D% 2>nul
mkdir %D%
cd %D%
del /q *
cd ..

cd ..
copy add_context_menu.reg %DIST%\%D%
copy remove_context_menu.reg %DIST%\%D%
copy installations.ini %DIST%\%D%
copy ewlaunch.ini %DIST%\%D%
copy README.md %DIST%\%D%
copy init_env.bat %DIST%\%D%
copy init_shell.bat %DIST%\%D%
move %DIST%\ewlaunch.exe %DIST%\%D%
move %DIST%\ewlaunch_win.exe %DIST%\%D%

cd %DIST%
%ZIP%  a -r %TGT% %D%
cd ..
