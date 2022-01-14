@echo off

:: ewlaunch only knows about workspaces, not projects
:: but it can be convenient to set PROJ_DIR anyway
set PROJ_DIR=%WS_DIR%

:: setup path
set PATH=%TOOLKIT_DIR%\bin;%EW_DIR%\common\bin;%PATH%

:: change directory to workspace directory
if not "%WS_DIR%"=="" cd %WS_DIR%
