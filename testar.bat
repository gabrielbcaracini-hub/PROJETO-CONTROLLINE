@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Rode primeiro o arquivo instalar.bat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest -q
pause
