@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title LMS Uniapp Auto Clicker
echo ===================================================
echo     KHOI DONG TOOL AUTO TEST LMS UNIAPP
echo ===================================================
echo.

python auto_test.py %*

echo.
pause
