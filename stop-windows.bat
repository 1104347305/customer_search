@echo off
setlocal enabledelayedexpansion

set PORT=%1
if "%PORT%"=="" set PORT=8000

set SCRIPT_DIR=%~dp0
set PID_FILE=%SCRIPT_DIR%logs\api_%PORT%.pid

echo ==========================================
echo Customer Search System - Windows Shutdown
echo ==========================================

:: Stop API service
if exist "%PID_FILE%" (
    set /p API_PID=<"%PID_FILE%"
    taskkill /F /PID !API_PID! >nul 2>&1
    if !errorlevel!==0 (
        echo [OK] API service stopped (PID: !API_PID!)
    ) else (
        echo     API process not found (PID: !API_PID!)
    )
    del "%PID_FILE%"
) else (
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
        taskkill /F /PID %%p >nul 2>&1
        echo [OK] API service stopped (PID: %%p)
        goto :stop_done
    )
    echo     No service running on port %PORT%
)
:stop_done

:: Stop Docker containers
echo.
echo Stopping Docker containers...
cd /d "%SCRIPT_DIR%docker"
docker-compose down
cd /d "%SCRIPT_DIR%"

echo.
echo [OK] All services stopped.
pause