@echo off
setlocal enabledelayedexpansion

set PORT=%1
if "%PORT%"=="" set PORT=8000

set SCRIPT_DIR=%~dp0
set LOG_FILE=%SCRIPT_DIR%logs\api_%PORT%.log
set PID_FILE=%SCRIPT_DIR%logs\api_%PORT%.pid

echo ==========================================
echo Customer Search System - Windows Startup
echo Port: %PORT%
echo ==========================================

if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

:: Detect Python
set PYTHON_CMD=
where python3 >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python3
) else (
    where python >nul 2>&1
    if !errorlevel!==0 (
        for /f %%v in ('python -c "import sys; print(sys.version_info.major)"') do set PY_VER=%%v
        if "!PY_VER!"=="3" set PYTHON_CMD=python
    )
)
if "!PYTHON_CMD!"=="" (
    echo [ERROR] Python 3 not found. Please install Python 3.8+ and add to PATH.
    pause
    exit /b 1
)
echo [OK] Python found: %PYTHON_CMD%

:: Detect Docker (check PATH first, then common install locations)
set DOCKER_CMD=
where docker >nul 2>&1
if %errorlevel%==0 (
    set DOCKER_CMD=docker
) else (
    if exist "C:\Program Files\Docker\Docker\resources\bin\docker.exe" (
        set DOCKER_CMD=C:\Program Files\Docker\Docker\resources\bin\docker.exe
    ) else if exist "%ProgramFiles%\Docker\Docker\resources\bin\docker.exe" (
        set DOCKER_CMD=%ProgramFiles%\Docker\Docker\resources\bin\docker.exe
    ) else if exist "%LOCALAPPDATA%\Programs\Docker\Docker\resources\bin\docker.exe" (
        set DOCKER_CMD=%LOCALAPPDATA%\Programs\Docker\Docker\resources\bin\docker.exe
    )
)
if "!DOCKER_CMD!"=="" (
    echo [ERROR] Docker not found. Please install Docker Desktop for Windows.
    echo         Download: https://www.docker.com/products/docker-desktop/
    echo         After installation, restart this CMD window and try again.
    pause
    exit /b 1
)
"!DOCKER_CMD!" info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo [OK] Docker is running

:: Check port
netstat -ano 2>nul | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo [ERROR] Port %PORT% is already in use. Run stop-windows.bat %PORT% first.
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%"

:: Step 1: Start Elasticsearch and Kibana
echo.
echo Step 1: Starting Elasticsearch and Kibana...
cd /d "%SCRIPT_DIR%docker"
docker-compose up -d elasticsearch kibana 2>nul || "!DOCKER_CMD!" compose up -d elasticsearch kibana
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker containers.
    pause
    exit /b 1
)
cd /d "%SCRIPT_DIR%"

echo Waiting for Elasticsearch (max 60s)...
set ES_READY=0
set /a TRIES=0
:wait_es
if %ES_READY%==1 goto :es_ok
set /a TRIES+=1
if %TRIES% gtr 30 goto :es_timeout
curl -s http://localhost:9200 >nul 2>&1
if %errorlevel%==0 (
    set ES_READY=1
    echo [OK] Elasticsearch is ready
    goto :es_ok
)
echo   Waiting... (%TRIES%/30)
timeout /t 2 /nobreak >nul
goto :wait_es

:es_timeout
echo [ERROR] Elasticsearch startup timeout. Check Docker Desktop.
pause
exit /b 1

:es_ok

:: Step 2: Generate mock data
echo.
if not exist "%SCRIPT_DIR%data\customers.json" (
    echo Step 2: Generating mock data (first run, ~30s)...
    %PYTHON_CMD% scripts\generate_mock_data.py
    if !errorlevel! neq 0 (
        echo [ERROR] Mock data generation failed.
        pause
        exit /b 1
    )
) else (
    echo Step 2: Mock data already exists, skipping.
)

:: Step 3: Init Elasticsearch index
echo.
echo Step 3: Initializing Elasticsearch index...
%PYTHON_CMD% scripts\init_elasticsearch.py
if %errorlevel% neq 0 (
    echo [ERROR] Index initialization failed.
    pause
    exit /b 1
)

:: Step 4: Import data
echo.
echo Step 4: Importing data to Elasticsearch...
%PYTHON_CMD% scripts\import_data.py
if %errorlevel% neq 0 (
    echo [ERROR] Data import failed.
    pause
    exit /b 1
)

:: Step 5: Start API service
echo.
echo Step 5: Starting API service...
start "CustomerSearch" /min cmd /c "uvicorn app.main:app --host 0.0.0.0 --port %PORT% >> %LOG_FILE% 2>&1"

echo Waiting for API service...
set API_READY=0
set /a TRIES=0
:wait_api
if %API_READY%==1 goto :api_ok
set /a TRIES+=1
if %TRIES% gtr 15 goto :api_timeout
curl -s http://localhost:%PORT%/health >nul 2>&1
if %errorlevel%==0 (
    set API_READY=1
    echo [OK] API service is ready
    goto :api_ok
)
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

echo.
echo ==========================================
echo [OK] All services started successfully!
echo ==========================================
echo   API Docs:    http://localhost:%PORT%/docs
echo   Health:      http://localhost:%PORT%/health
echo   Kibana:      http://localhost:5601
echo   Log file:    %LOG_FILE%
echo   To stop:     stop-windows.bat %PORT%
echo ==========================================
pause
