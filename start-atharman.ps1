#!/usr/bin/env powershell
<#
.SYNOPSIS
    Atharman Platform Startup Script
.DESCRIPTION
    Starts both frontend and backend services for the Atharman AI Cloud Intelligence Platform
.EXAMPLE
    .\start-atharman.ps1
#>

param(
    [Parameter()]
    [switch]$SkipInstall,
    
    [Parameter()]
    [switch]$Development,
    
    [Parameter()]
    [int]$BackendPort = 5000,
    
    [Parameter()]
    [int]$FrontendPort = 3000
)

# Color output functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Python
    try {
        $pythonVersion = & python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Error "Python not found. Please install Python 3.8+ and add to PATH"
        return $false
    }
    
    # Check Node.js
    try {
        $nodeVersion = & node --version 2>&1
        Write-Success "Node.js found: $nodeVersion"
    } catch {
        Write-Error "Node.js not found. Please install Node.js 16+ and add to PATH"
        return $false
    }
    
    # Check if virtual environment exists
    if (Test-Path ".venv") {
        Write-Success "Python virtual environment found"
    } else {
        Write-Warning "Python virtual environment not found - will create one"
    }
    
    return $true
}

function Setup-PythonEnvironment {
    if (-not $SkipInstall) {
        Write-Info "Setting up Python environment..."
        
        if (-not (Test-Path ".venv")) {
            Write-Info "Creating Python virtual environment..."
            python -m venv .venv
        }
        
        Write-Info "Activating virtual environment..."
        & ".venv\Scripts\Activate.ps1"
        
        Write-Info "Installing Python dependencies..."
        python -m pip install --upgrade pip setuptools wheel
        
        if (Test-Path "requirements-minimal.txt") {
            Write-Info "Installing minimal requirements for faster startup..."
            pip install -r requirements-minimal.txt
        } elseif (Test-Path "requirements-production.txt") {
            Write-Info "Installing production requirements..."
            pip install -r requirements-production.txt
        } else {
            Write-Warning "No requirements file found - installing basic packages..."
            pip install flask flask-cors waitress pandas numpy
        }
        
        Write-Success "Python environment ready!"
    }
}

function Setup-NodeEnvironment {
    if (-not $SkipInstall) {
        Write-Info "Setting up Node.js environment..."
        
        if (-not (Test-Path "frontend\node_modules")) {
            Write-Info "Installing Node.js dependencies..."
            Set-Location frontend
            npm install
            Set-Location ..
            Write-Success "Node.js dependencies installed!"
        } else {
            Write-Success "Node.js dependencies already installed"
        }
    }
}

function Start-Backend {
    Write-Info "Starting Atharman backend server on port $BackendPort..."
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Set environment variables
    $env:PORT = $BackendPort
    $env:HOST = "0.0.0.0"
    
    if ($Development) {
        Write-Info "Starting in development mode with debug logging..."
        $env:DEBUG = "true"
        $env:LOG_LEVEL = "DEBUG"
    }
    
    # Start backend in background
    $backendJob = Start-Job -ScriptBlock {
        param($port, $dev)
        Set-Location $using:PWD
        & ".venv\Scripts\Activate.ps1"
        $env:PORT = $port
        if ($dev) { $env:DEBUG = "true" }
        python production_server.py
    } -ArgumentList $BackendPort, $Development
    
    Write-Success "Backend server starting... (Job ID: $($backendJob.Id))"
    return $backendJob
}

function Start-Frontend {
    Write-Info "Starting Atharman frontend on port $FrontendPort..."
    
    # Set environment variables for frontend
    $env:REACT_APP_API_URL = "http://localhost:$BackendPort"
    $env:PORT = $FrontendPort
    
    # Start frontend in background
    $frontendJob = Start-Job -ScriptBlock {
        param($port, $apiUrl)
        Set-Location "$using:PWD\frontend"
        $env:PORT = $port
        $env:REACT_APP_API_URL = $apiUrl
        npm start
    } -ArgumentList $FrontendPort, "http://localhost:$BackendPort"
    
    Write-Success "Frontend starting... (Job ID: $($frontendJob.Id))"
    return $frontendJob
}

function Wait-ForServices {
    param($BackendJob, $FrontendJob)
    
    Write-Info "Waiting for services to start..."
    
    # Wait for backend
    $backendReady = $false
    $frontendReady = $false
    $maxAttempts = 30
    $attempt = 0
    
    while ((-not $backendReady -or -not $frontendReady) -and $attempt -lt $maxAttempts) {
        Start-Sleep 2
        $attempt++
        
        # Check backend health
        if (-not $backendReady) {
            try {
                $response = Invoke-RestMethod -Uri "http://localhost:$BackendPort/health" -TimeoutSec 5
                if ($response.status -eq "healthy") {
                    Write-Success "Backend is ready!"
                    $backendReady = $true
                }
            } catch {
                Write-Host "." -NoNewline
            }
        }
        
        # Check frontend
        if (-not $frontendReady) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$FrontendPort" -TimeoutSec 5
                if ($response.StatusCode -eq 200) {
                    Write-Success "Frontend is ready!"
                    $frontendReady = $true
                }
            } catch {
                Write-Host "." -NoNewline
            }
        }
    }
    
    if ($backendReady -and $frontendReady) {
        Write-Success "🎉 Atharman platform is ready!"
        Write-Info ""
        Write-Info "📊 Access your dashboard at: http://localhost:$FrontendPort"
        Write-Info "🔧 Backend API available at: http://localhost:$BackendPort"
        Write-Info "💡 Health check: http://localhost:$BackendPort/health"
        Write-Info ""
        Write-Warning "Press Ctrl+C to stop all services"
        return $true
    } else {
        Write-Error "Services failed to start within timeout period"
        return $false
    }
}

function Stop-Services {
    param($BackendJob, $FrontendJob)
    
    Write-Info "Stopping services..."
    
    if ($BackendJob) {
        Stop-Job $BackendJob -ErrorAction SilentlyContinue
        Remove-Job $BackendJob -ErrorAction SilentlyContinue
        Write-Success "Backend stopped"
    }
    
    if ($FrontendJob) {
        Stop-Job $FrontendJob -ErrorAction SilentlyContinue
        Remove-Job $FrontendJob -ErrorAction SilentlyContinue
        Write-Success "Frontend stopped"
    }
}

# Main execution
try {
    Write-Info "🚀 Starting Atharman AI Cloud Intelligence Platform..."
    Write-Info "=================================================="
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    # Setup environments
    Setup-PythonEnvironment
    Setup-NodeEnvironment
    
    # Start services
    $backendJob = Start-Backend
    Start-Sleep 3  # Give backend a head start
    $frontendJob = Start-Frontend
    
    # Wait for services and show status
    if (Wait-ForServices -BackendJob $backendJob -FrontendJob $frontendJob) {
        # Keep running until interrupted
        try {
            while ($true) {
                Start-Sleep 1
                
                # Check if jobs are still running
                if ($backendJob.State -ne "Running") {
                    Write-Error "Backend service stopped unexpectedly"
                    break
                }
                
                if ($frontendJob.State -ne "Running") {
                    Write-Error "Frontend service stopped unexpectedly"
                    break
                }
            }
        } catch {
            Write-Info "Shutdown requested..."
        }
    }
    
} catch {
    Write-Error "Startup failed: $($_.Exception.Message)"
} finally {
    Stop-Services -BackendJob $backendJob -FrontendJob $frontendJob
    Write-Info "Atharman platform stopped."
}