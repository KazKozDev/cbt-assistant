@echo off
setlocal

cd /d "%~dp0"
title CBT Assistant - automatic Windows setup

echo.
echo CBT ASSISTANT
echo Local AI CBT companion - automatic Windows setup
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_cbt_assistant_windows.ps1"
set "CBT_EXIT_CODE=%ERRORLEVEL%"

if not "%CBT_EXIT_CODE%"=="0" (
    echo.
    echo CBT Assistant stopped with exit code %CBT_EXIT_CODE%.
    pause
)

exit /b %CBT_EXIT_CODE%
