@echo off
setlocal

set "TASK_OFFLINE=Blitztext-Offline"
set "TASK_HYBRID=Blitztext-Hybrid"
set "BASE_DIR=%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_OFFLINE=%STARTUP_DIR%\Blitztext-Offline-Autostart.cmd"
set "STARTUP_HYBRID=%STARTUP_DIR%\Blitztext-Hybrid-Autostart.cmd"

for %%I in ("%BASE_DIR%..\.venv\Scripts\python.exe") do set "PYTHON_EXE=%%~fI"
for %%I in ("%BASE_DIR%app.py") do set "APP_FILE=%%~fI"

if "%OPENAI_API_KEY%"=="" (
  echo OPENAI_API_KEY ist nicht gesetzt.
  echo Bitte zuerst den API Key als Benutzer-Umgebungsvariable setzen.
  echo Beispiel: setx OPENAI_API_KEY "dein_key_hier"
  pause
  exit /b 1
)

if not exist "%PYTHON_EXE%" (
  echo Python Umgebung nicht gefunden: "%PYTHON_EXE%"
  pause
  exit /b 1
)

if not exist "%APP_FILE%" (
  echo App-Datei nicht gefunden: "%APP_FILE%"
  pause
  exit /b 1
)

rem Nur ein Modus soll beim Login laufen.
schtasks /Delete /TN "%TASK_OFFLINE%" /F >nul 2>&1
schtasks /Delete /TN "%TASK_HYBRID%" /F >nul 2>&1
del /Q "%STARTUP_OFFLINE%" >nul 2>&1
del /Q "%STARTUP_HYBRID%" >nul 2>&1

set "ACTION=\"%PYTHON_EXE%\" \"%APP_FILE%\" --offline --rewrite --rewrite-model gpt-4o-mini"

schtasks /Create /TN "%TASK_HYBRID%" /SC ONLOGON /TR "%ACTION%" /RL LIMITED /F >nul
if errorlevel 1 (
  echo Task Scheduler nicht verfuegbar. Nutze Startup-Ordner-Fallback...
  > "%STARTUP_HYBRID%" echo @echo off
  >> "%STARTUP_HYBRID%" echo start "Blitztext Hybrid" /min "%PYTHON_EXE%" "%APP_FILE%" --offline --rewrite --rewrite-model gpt-4o-mini
  if not exist "%STARTUP_HYBRID%" (
    echo Konnte weder Task noch Startup-Fallback einrichten.
    pause
    exit /b 1
  )
  echo Autostart aktiviert: HYBRID ^(Startup-Ordner Fallback^)
  echo Datei: %STARTUP_HYBRID%
  echo.
  echo Hinweis: Beim naechsten Login startet Blitztext automatisch.
  pause
  exit /b 0
)

echo Autostart aktiviert: HYBRID
echo Task: %TASK_HYBRID%
echo.
echo Hinweis: Beim naechsten Login startet Blitztext automatisch.
pause
