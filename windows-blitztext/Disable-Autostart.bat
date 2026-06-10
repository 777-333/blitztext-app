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

schtasks /Delete /TN "%TASK_OFFLINE%" /F >nul 2>&1
schtasks /Delete /TN "%TASK_HYBRID%" /F >nul 2>&1
schtasks /Delete /TN "%TASK_TRAY_OFFLINE%" /F >nul 2>&1
schtasks /Delete /TN "%TASK_TRAY_HYBRID%" /F >nul 2>&1
del /Q "%STARTUP_OFFLINE%" >nul 2>&1
del /Q "%STARTUP_HYBRID%" >nul 2>&1
del /Q "%STARTUP_TRAY_OFFLINE%" >nul 2>&1
del /Q "%STARTUP_TRAY_HYBRID%" >nul 2>&1

echo Autostart deaktiviert (Task Scheduler und Startup-Fallback bereinigt).
pause
