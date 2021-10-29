@echo off
setlocal
REM Tested with Python: 3.9.7, PyInstaller: 4.5.1

set VERSION=%1
set ZIP="C:\Program Files\WinRAR\WinRar.exe"
set DIST=dist
set D=ewlaunch-%VERSION%
set TGT=%D%.zip

pyinstaller --windowed --onefile ewlaunch.py --icon=ewlaunch.ico

cd %DIST%
del /q %TGT%
rmdir /q /s %D%
mkdir %D%
cd %D%
del /q *
cd ..

cd ..
copy installations.ini %DIST%\%D%
copy ewlaunch.ini %DIST%\%D%
copy README.md %DIST%\%D%
move %DIST%\ewlaunch.exe %DIST%\%D%

cd %DIST%
%ZIP%  a -r %TGT% %D%
cd ..
