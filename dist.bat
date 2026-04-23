@echo off
setlocal
REM Tested with Python: 3.14.4

set VERSION=%1
set ZIP="C:\Program Files\WinRAR\WinRar.exe"
set DIST=dist
set D=ewlaunch-%VERSION%
set TGT=%D%.zip

pyinstaller --windowed ewlaunch_win.py --icon=ewlaunch.ico
pyinstaller ewlaunch.py

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
move %DIST%\ewlaunch\ewlaunch.exe %DIST%\%D%
move %DIST%\ewlaunch_win\ewlaunch_win.exe %DIST%\%D%
move %DIST%\ewlaunch_win\_internal %DIST%\%D%

cd %DIST%
%ZIP%  a -r %TGT% %D%
cd ..
