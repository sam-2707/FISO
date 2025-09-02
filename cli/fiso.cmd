@echo off
REM FISO CLI Launcher for Windows
REM This script allows you to run 'fiso' from anywhere

set FISO_ROOT=%~dp0..
set PYTHON_PATH=%FISO_ROOT%\.venv\Scripts\python.exe
set CLI_SCRIPT=%FISO_ROOT%\cli\fiso.py

REM Check if Python environment exists
if not exist "%PYTHON_PATH%" (
    echo Error: Python virtual environment not found at %PYTHON_PATH%
    echo Please run the setup script first.
    exit /b 1
)

REM Check if CLI script exists
if not exist "%CLI_SCRIPT%" (
    echo Error: FISO CLI script not found at %CLI_SCRIPT%
    exit /b 1
)

REM Run the CLI with all arguments
"%PYTHON_PATH%" "%CLI_SCRIPT%" %*
