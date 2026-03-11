@echo off
setlocal enabledelayedexpansion

set PORT=%1
if "%PORT%"=="" set PORT=8000

set SCRIPT_DIR=%~dp0
set PID_FILE=%SCRIPT_DIR%logs\api_%PORT%.pid

echo ==========================================
echo Customer Search System - Shutdown (No Docker)
echo ==========================================

:: Stop API service only (ES managed separately)
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

echo.
echo [OK] API service stopped.
echo     Note: Elasticsearch is not stopped. Close its window manually if needed.
pause
