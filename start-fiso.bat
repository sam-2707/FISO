@echo off
:: ===================================================================
:: FISO Full Stack Startup Script (Batch Version)
:: Launches both frontend and backend components of the FISO platform
:: ===================================================================

setlocal enabledelayedexpansion

:: Configuration
set BACKEND_PORT=5000
set FRONTEND_PORT=3000
set MODE=dev

:: Color codes for output
set "COLOR_INFO=96"
set "COLOR_SUCCESS=92"
set "COLOR_ERROR=91"
set "COLOR_WARNING=93"

:: Parse command line arguments
:parse_args
if "%~1"=="" goto :check_environment
if /i "%~1"=="--prod" set MODE=prod
if /i "%~1"=="--dev" set MODE=dev
if /i "%~1"=="--backend-port" set BACKEND_PORT=%~2& shift
if /i "%~1"=="--frontend-port" set FRONTEND_PORT=%~2& shift
if /i "%~1"=="--help" goto :show_help
shift
goto :parse_args

:show_help
echo.
echo FISO Full Stack Startup Script
echo ===============================
echo.
echo Usage: start-fiso.bat [options]
echo.
echo Options:
echo   --dev              Start in development mode (default)
echo   --prod             Start in production mode
echo   --backend-port N   Set backend port (default: 5000)
echo   --frontend-port N  Set frontend port (default: 3000)
echo   --help             Show this help message
echo.
echo Examples:
echo   start-fiso.bat
echo   start-fiso.bat --prod
echo   start-fiso.bat --backend-port 8080 --frontend-port 3001
echo.
goto :eof

:check_environment
cls
echo.
call :print_info "FISO Full Stack Startup Script"
call :print_info "==============================="
echo.

:: Check if we're in the right directory
if not exist "package.json" (
    call :print_error "package.json not found. Please run this script from the FISO root directory."
    goto :error_exit
)

if not exist "production_server.py" (
    call :print_error "production_server.py not found. Please run this script from the FISO root directory."
    goto :error_exit
)

:: Check Node.js
call :print_info "Checking Node.js installation..."
node --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Node.js not found. Please install Node.js from https://nodejs.org/"
    goto :error_exit
) else (
    for /f "tokens=*" %%i in ('node --version 2^>nul') do (
        call :print_success "Node.js found: %%i"
    )
)

:: Check Python
call :print_info "Checking Python installation..."
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python not found. Please install Python from https://python.org/"
    goto :error_exit
) else (
    for /f "tokens=*" %%i in ('python --version 2^>nul') do (
        call :print_success "Python found: %%i"
    )
)

:: Install dependencies
call :print_info "Installing dependencies..."

:: Python dependencies
if exist "requirements-production.txt" (
    call :print_info "Installing Python dependencies..."
    pip install -r requirements-production.txt
    if errorlevel 1 (
        call :print_error "Failed to install Python dependencies"
        goto :error_exit
    )
)

:: Root Node.js dependencies
if exist "package.json" (
    call :print_info "Installing root Node.js dependencies..."
    call npm install
    if errorlevel 1 (
        call :print_error "Failed to install root Node.js dependencies"
        goto :error_exit
    )
)

:: Frontend dependencies
if exist "frontend\package.json" (
    call :print_info "Installing frontend dependencies..."
    pushd frontend
    call npm install
    if errorlevel 1 (
        call :print_error "Failed to install frontend dependencies"
        popd
        goto :error_exit
    )
    popd
)

call :print_success "All dependencies installed successfully!"
echo.

:: Start the services
call :print_info "Starting FISO Platform..."
call :print_info "Mode: %MODE%"
call :print_info "Backend Port: %BACKEND_PORT%"
call :print_info "Frontend Port: %FRONTEND_PORT%"
echo.

:: Set environment variables
set FLASK_ENV=%MODE%
if "%MODE%"=="dev" set FLASK_ENV=development
if "%MODE%"=="prod" set FLASK_ENV=production

:: Create startup commands
set "BACKEND_CMD=python production_server.py"
set "FRONTEND_CMD=cd frontend && npm start"

if "%MODE%"=="prod" (
    set "FRONTEND_CMD=cd frontend && npm run build && npx serve -s build -l %FRONTEND_PORT%"
)

:: Start backend in a new window
call :print_info "Starting backend server..."
start "FISO Backend" cmd /k "set PORT=%BACKEND_PORT% && set FLASK_ENV=%FLASK_ENV% && %BACKEND_CMD%"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
call :print_info "Starting frontend server..."
start "FISO Frontend" cmd /k "set PORT=%FRONTEND_PORT% && %FRONTEND_CMD%"

echo.
call :print_success "🚀 FISO Platform is starting up..."
call :print_success "📊 Frontend: http://localhost:%FRONTEND_PORT%"
call :print_success "🔧 Backend API: http://localhost:%BACKEND_PORT%"
echo.
call :print_info "Both services are running in separate windows."
call :print_info "Close the respective windows to stop the services."
echo.
pause
goto :eof

:: Helper functions for colored output
:print_info
powershell -Command "Write-Host '%~1' -ForegroundColor Cyan"
goto :eof

:print_success
powershell -Command "Write-Host '✅ %~1' -ForegroundColor Green"
goto :eof

:print_error
powershell -Command "Write-Host '❌ %~1' -ForegroundColor Red"
goto :eof

:print_warning
powershell -Command "Write-Host '⚠️ %~1' -ForegroundColor Yellow"
goto :eof

:error_exit
echo.
call :print_error "Script execution failed. Please check the errors above."
pause
exit /b 1