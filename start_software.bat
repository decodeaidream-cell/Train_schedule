@echo off
setlocal

echo ==============================================
echo   IRCTC Automator - Suhail Edition v2.0
echo   Starting... Please wait.
echo ==============================================

:: Check if python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

:: Check if venv exists and is healthy
if not exist venv\Scripts\python.exe goto :build_venv

echo [CHECK] Verifying Virtual Environment health...
venv\Scripts\python.exe -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] Broken or copied venv detected. Rebuilding...
    rmdir /s /q venv
    goto :build_venv
)

echo [OK] Virtual Environment is healthy.
goto :install_deps

:build_venv
echo [SETUP] Creating fresh Virtual Environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b
)

:install_deps
echo [SETUP] Installing / verifying dependencies...
venv\Scripts\python.exe -m pip install -r backend\requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Dependency installation failed. Check your internet connection.
    pause
    exit /b
)
echo [OK] All dependencies are ready.

:: Start FastAPI Backend
echo [START] Launching Backend on http://127.0.0.1:8000 ...
start "IRCTC Backend" cmd /k "cd /d "%CD%\backend" && "%CD%\venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000"

:: Start Frontend HTTP Server (Fixes CORS file:// errors)
echo [START] Launching Frontend on http://127.0.0.1:8080 ...
start "IRCTC Frontend" cmd /k "cd /d "%CD%\frontend" && "%CD%\venv\Scripts\python.exe" -m http.server 8080"

:: Wait for servers to be ready
timeout /t 5 >nul

:: Open browser using HTTP instead of file://
echo [OPEN]  Opening http://127.0.0.1:8080 in browser...
start "" "http://127.0.0.1:8080"

echo.
echo ==============================================
echo   Backend  : http://127.0.0.1:8000
echo   Frontend : http://127.0.0.1:8080
echo   Close the two black windows to stop.
echo ==============================================
