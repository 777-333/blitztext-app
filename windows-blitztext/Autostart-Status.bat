@echo off
setlocal

set "TASK_OFFLINE=Blitztext-Offline"
set "TASK_HYBRID=Blitztext-Hybrid"
set "TASK_TRAY_OFFLINE=Blitztext-Tray-Offline"
set "TASK_TRAY_HYBRID=Blitztext-Tray-Hybrid"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_OFFLINE=%STARTUP_DIR%\Blitztext-Offline-Autostart.cmd"
set "STARTUP_HYBRID=%STARTUP_DIR%\Blitztext-Hybrid-Autostart.cmd"
set "STARTUP_TRAY_OFFLINE=%STARTUP_DIR%\Blitztext-Tray-Offline-Autostart.cmd"
set "STARTUP_TRAY_HYBRID=%STARTUP_DIR%\Blitztext-Tray-Hybrid-Autostart.cmd"

echo === Blitztext Autostart Status ===
echo.

schtasks /Query /TN "%TASK_OFFLINE%" >nul 2>&1
if errorlevel 1 (
  echo Offline Task Scheduler: NICHT AKTIV
) else (
  echo Offline Task Scheduler: AKTIV
)

schtasks /Query /TN "%TASK_HYBRID%" >nul 2>&1
if errorlevel 1 (
  echo Hybrid Task Scheduler: NICHT AKTIV
) else (
  echo Hybrid Task Scheduler: AKTIV
)

schtasks /Query /TN "%TASK_TRAY_OFFLINE%" >nul 2>&1
if errorlevel 1 (
  echo Tray Offline Task Scheduler: NICHT AKTIV
) else (
  echo Tray Offline Task Scheduler: AKTIV
)

schtasks /Query /TN "%TASK_TRAY_HYBRID%" >nul 2>&1
if errorlevel 1 (
  echo Tray Hybrid Task Scheduler: NICHT AKTIV
) else (
  echo Tray Hybrid Task Scheduler: AKTIV
)

if exist "%STARTUP_OFFLINE%" (
  echo Offline Startup-Fallback: AKTIV
) else (
  echo Offline Startup-Fallback: NICHT AKTIV
)

if exist "%STARTUP_HYBRID%" (
  echo Hybrid Startup-Fallback: AKTIV
) else (
  echo Hybrid Startup-Fallback: NICHT AKTIV
)

if exist "%STARTUP_TRAY_OFFLINE%" (
  echo Tray Offline Startup-Fallback: AKTIV
) else (
  echo Tray Offline Startup-Fallback: NICHT AKTIV
)

if exist "%STARTUP_TRAY_HYBRID%" (
  echo Tray Hybrid Startup-Fallback: AKTIV
) else (
  echo Tray Hybrid Startup-Fallback: NICHT AKTIV
)

echo.
echo Tipp:
echo - Enable-Autostart-Offline.bat
echo - Enable-Autostart-Hybrid.bat
echo - Enable-Autostart-Tray-Offline.bat
echo - Enable-Autostart-Tray-Hybrid.bat
echo - Disable-Autostart.bat
pause
