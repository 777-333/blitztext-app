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

start "Blitztext Tray Offline" /min "%PYTHON_EXE%" "%APP_FILE%" --offline --offline-model small --tray
