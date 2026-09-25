@echo off
setlocal
cd /d "%~dp0"
title LineControl - instalar

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY=python"
  ) else (
    echo Instale o Python 3.10 ou superior:
    echo https://www.python.org/downloads/
    echo Marque a opcao Add python.exe to PATH.
    pause
    exit /b 1
  )
)

echo Criando ambiente local nesta pasta...
%PY% -m venv .venv
if errorlevel 1 (
  echo Nao foi possivel criar o ambiente. Confira a instalacao do Python.
  pause
  exit /b 1
)

echo Instalando os pacotes da pasta dependencias...
".venv\Scripts\python.exe" -m pip install --no-index --find-links=dependencias -r requirements.txt
if errorlevel 1 (
  echo Falha ao instalar. Use Python 3.10, 3.11, 3.12 ou 3.13.
  pause
  exit /b 1
)

echo.
echo Instalacao concluida. Agora abra executar.bat
pause
