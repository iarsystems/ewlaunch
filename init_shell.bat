@echo off
:: Customization for shell started with "ewlaunch.exe shell"

if "%WS_FNAME%"=="" (title %EW_VERSION%) else (title %EW_VERSION% - %WS_FNAME%)

call %~dp0\init_env.bat

echo [90mRunning %0 ...
echo.
echo   EW_VERSION  - %EW_VERSION%
echo   WS_PATH     - %WS_PATH%
::echo   WS_BPATH    - %WS_BPATH%
::echo   WS_FNAME    - %WS_FNAME%
::echo   WS_BNAME    - %WS_BNAME%
::echo   WS_DIR      - %WS_DIR%
echo   EW_DIR      - %EW_DIR%
::echo   TOOLKIT     - %TOOLKIT%
echo   TOOLKIT_DIR - %TOOLKIT_DIR%[0m