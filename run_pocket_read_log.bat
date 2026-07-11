@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0pocket_read_log.ps1"
echo.
echo Press any key to close this window...
pause >nul
