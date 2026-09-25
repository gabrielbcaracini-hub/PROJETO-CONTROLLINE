@echo off
setlocal
cd /d "%~dp0"
title LineControl

if not exist ".venv\Scripts\python.exe" (
  echo Rode primeiro o arquivo instalar.bat
  pause
  exit /b 1
)

echo Encerrando instancia antiga na porta 8741, se existir...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8741 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo Abrindo o sistema em http://127.0.0.1:8741
".venv\Scripts\python.exe" run.py
pause
