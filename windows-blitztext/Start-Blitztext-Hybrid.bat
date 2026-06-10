@echo off
setlocal

set "BASE_DIR=%~dp0"
set "PYTHON_EXE=%BASE_DIR%..\.venv\Scripts\python.exe"
set "APP_FILE=%BASE_DIR%app.py"

if not exist "%PYTHON_EXE%" (
  echo Python Umgebung nicht gefunden: "%PYTHON_EXE%"
  echo Bitte zuerst die Abhaengigkeiten installieren.
  pause
  exit /b 1
)

if not exist "%APP_FILE%" (
  echo App-Datei nicht gefunden: "%APP_FILE%"
  pause
  exit /b 1
)

if "%OPENAI_API_KEY%"=="" (
  echo OPENAI_API_KEY ist nicht gesetzt.
  echo Fuer Hybrid-Modus bitte zuerst den API Key setzen.
  pause
  exit /b 1
)

start "Blitztext Hybrid" /min "%PYTHON_EXE%" "%APP_FILE%" --offline --rewrite --rewrite-model gpt-4o-mini
