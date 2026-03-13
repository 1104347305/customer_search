@echo off

set PORT=%1
if "%PORT%"=="" set PORT=8000

set SCRIPT_DIR=%~dp0
set LOG_FILE=%SCRIPT_DIR%logs\api_%PORT%.log
set PID_FILE=%SCRIPT_DIR%logs\api_%PORT%.pid
set PYTHON_CMD=

echo ==========================================
echo Customer Search System - Startup (No Docker)
echo Port: %PORT%
echo ==========================================

if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

rem --- Detect Python ---
where python3 >nul 2>&1
if %errorlevel%==0 goto :found_python3
where python >nul 2>&1
if %errorlevel%==0 goto :found_python
echo [ERROR] Python 3 not found. Please install Python 3.8+ and add to PATH.
pause
exit /b 1

:found_python3
set PYTHON_CMD=python3
goto :python_ok

:found_python
set PYTHON_CMD=python
goto :python_ok

:python_ok
echo [OK] Python found: %PYTHON_CMD%

rem --- Step 0: Install dependencies ---
echo.
echo Step 0: Installing Python dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt -q --user
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies ready.

rem --- Check port ---
netstat -ano 2>nul | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 goto :port_busy
goto :port_ok

:port_busy
echo [ERROR] Port %PORT% is already in use.
pause
exit /b 1

:port_ok
cd /d "%SCRIPT_DIR%"

rem --- Step 1: Check Elasticsearch ---
echo.
echo Step 1: Checking Elasticsearch...
curl -s http://localhost:9200 >nul 2>&1
if %errorlevel%==0 goto :es_ok

echo [ERROR] Elasticsearch is not running on localhost:9200
echo.
echo Please start Elasticsearch first:
echo   1. Download: https://www.elastic.co/downloads/elasticsearch
echo   2. Extract and run: C:\elasticsearch\bin\elasticsearch.bat
echo   3. Wait for startup, then run this script again.
pause
exit /b 1

:es_ok
echo [OK] Elasticsearch is running

rem --- Step 2: Generate mock data ---
echo.
if exist "%SCRIPT_DIR%data\customers.json" goto :data_ok

echo Step 2: Generating mock data (first run, ~30s)...
%PYTHON_CMD% scripts\generate_mock_data.py
if %errorlevel% neq 0 goto :data_fail
goto :data_ok

:data_fail
echo [ERROR] Mock data generation failed.
pause
exit /b 1

:data_ok
echo Step 2: Mock data ready.

rem --- Step 3: Init ES index ---
echo.
echo Step 3: Initializing Elasticsearch index...
%PYTHON_CMD% scripts\init_elasticsearch.py
if %errorlevel% neq 0 goto :init_fail
goto :init_ok

:init_fail
echo [ERROR] Index initialization failed.
pause
exit /b 1

:init_ok

rem --- Step 4: Import data ---
echo.
echo Step 4: Importing data to Elasticsearch...
%PYTHON_CMD% scripts\import_data.py
if %errorlevel% neq 0 goto :import_fail
goto :import_ok

:import_fail
echo [ERROR] Data import failed.
pause
exit /b 1

:import_ok

rem --- Step 5: Start API ---
echo.
echo Step 5: Starting API service...
start "CustomerSearch" /min cmd /c "uvicorn app.main:app --host 0.0.0.0 --port %PORT% >> %LOG_FILE% 2>&1"

echo Waiting for API service...
set TRIES=0

:wait_api
set /a TRIES=%TRIES%+1
if %TRIES% gtr 15 goto :api_timeout
curl -s http://localhost:%PORT%/health >nul 2>&1
if %errorlevel%==0 goto :api_ok
timeout /t 1 /nobreak >nul
goto :wait_api

:api_timeout
echo [ERROR] API service failed to start. Check log: %LOG_FILE%
pause
exit /b 1

:api_ok
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    echo %%p>"%PID_FILE%"
    goto :pid_saved
)
:pid_saved

echo [OK] API service is ready
echo.
echo ==========================================
echo [OK] All services started successfully!
echo ==========================================
echo   API Docs:    http://localhost:%PORT%/docs
echo   Health:      http://localhost:%PORT%/health
echo   Log file:    %LOG_FILE%
echo   To stop:     stop-windows-nodocker.bat %PORT%
echo ==========================================
pause
