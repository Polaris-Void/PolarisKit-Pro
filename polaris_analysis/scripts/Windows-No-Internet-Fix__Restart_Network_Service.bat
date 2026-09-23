@echo off
if "%~1"=="admin" goto :run
powershell -Command "Start-Process '%~f0' 'admin' -Verb RunAs" & exit /b

:run
net stop NlaSvc /y
net start NlaSvc
timeout /t 5 >nul
exit