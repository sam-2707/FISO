#!/usr/bin/env pwsh
<#
.SYNOPSIS
    FISO Full Stack Startup Script
.DESCRIPTION
    Launches both frontend and backend components of the FISO platform
.PARAMETER Mode
    Startup mode: 'dev' for development, 'prod' for production
.PARAMETER Frontend
    Start only frontend (React development server)
.PARAMETER Backend
    Start only backend (Python production server)
.PARAMETER Port
    Backend port (default: 5000)
.PARAMETER FrontendPort
    Frontend port (default: 3000)
.EXAMPLE
    .\start-fiso.ps1 -Mode dev
    .\start-fiso.ps1 -Mode prod
    .\start-fiso.ps1 -Frontend
    .\start-fiso.ps1 -Backend -Port 8080
#>

param(
    [Parameter()]
    [ValidateSet('dev', 'prod')]
    [string]$Mode = 'dev',
    
    [Parameter()]
    [switch]$Frontend,
    
    [Parameter()]
    [switch]$Backend,
    
    [Parameter()]
    [int]$Port = 5000,
    
    [Parameter()]
    [int]$FrontendPort = 3000
)

# Color functions for better output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Info($message) {
    Write-ColorOutput Cyan "ℹ️  $message"
}

function Write-Success($message) {
    Write-ColorOutput Green "✅ $message"
}

function Write-Error($message) {
    Write-ColorOutput Red "❌ $message"
}

function Write-Warning($message) {
    Write-ColorOutput Yellow "⚠️  $message"
}

# Check if we're in the right directory
if (-not (Test-Path "package.json") -or -not (Test-Path "production_server.py")) {
    Write-Error "Please run this script from the FISO root directory"
    exit 1
}

Write-Info "FISO Full Stack Startup Script"
Write-Info "==============================="

# Function to check if Node.js is installed
function Test-NodeJS {
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-Success "Node.js found: $nodeVersion"
            return $true
        }
    } catch {
        Write-Error "Node.js not found. Please install Node.js from https://nodejs.org/"
        return $false
    }
    return $false
}

# Function to check if Python is installed
function Test-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Success "Python found: $pythonVersion"
            return $true
        }
    } catch {
        Write-Error "Python not found. Please install Python from https://python.org/"
        return $false
    }
    return $false
}

# Function to install dependencies
function Install-Dependencies {
    Write-Info "Checking and installing dependencies..."
    
    # Install Python dependencies
    if (Test-Path "requirements-production.txt") {
        Write-Info "Installing Python dependencies..."
        pip install -r requirements-production.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install Python dependencies"
            return $false
        }
    }
    
    # Install root Node.js dependencies
    if (Test-Path "package.json") {
        Write-Info "Installing root Node.js dependencies..."
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install root Node.js dependencies"
            return $false
        }
    }
    
    # Install frontend dependencies
    if (Test-Path "frontend/package.json") {
        Write-Info "Installing frontend dependencies..."
        Push-Location frontend
        npm install
        $success = $LASTEXITCODE -eq 0
        Pop-Location
        if (-not $success) {
            Write-Error "Failed to install frontend dependencies"
            return $false
        }
    }
    
    return $true
}

# Function to start backend server
function Start-Backend {
    param([int]$BackendPort = 5000)
    
    Write-Info "Starting FISO Backend Server on port $BackendPort..."
    
    # Set environment variables
    $env:FLASK_ENV = if ($Mode -eq 'dev') { 'development' } else { 'production' }
    $env:PORT = $BackendPort
    
    # Start the appropriate server
    if ($Mode -eq 'dev') {
        Write-Info "Starting development server..."
        python production_server.py --dev --port $BackendPort
    } else {
        Write-Info "Starting production server..."
        python production_server.py --port $BackendPort
    }
}

# Function to start frontend server
function Start-Frontend {
    param([int]$FrontendPort = 3000)
    
    Write-Info "Starting FISO Frontend Server on port $FrontendPort..."
    
    Push-Location frontend
    
    # Set frontend port
    $env:PORT = $FrontendPort
    
    if ($Mode -eq 'dev') {
        Write-Info "Starting React development server..."
        npm run frontend
    } else {
        Write-Info "Building and serving production frontend..."
        npm run build
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Serving built frontend..."
            npx serve -s build -l $FrontendPort
        } else {
            Write-Error "Frontend build failed"
            Pop-Location
            return $false
        }
    }
    
    Pop-Location
    return $true
}

# Function to start both frontend and backend
function Start-FullStack {
    Write-Info "Starting Full Stack FISO Platform..."
    Write-Info "Mode: $Mode"
    Write-Info "Backend Port: $Port"
    Write-Info "Frontend Port: $FrontendPort"
    
    # Create background jobs for both servers
    $backendJob = Start-Job -ScriptBlock {
        param($scriptPath, $mode, $port)
        Set-Location (Split-Path $scriptPath)
        & $scriptPath -Backend -Mode $mode -Port $port
    } -ArgumentList $PSCommandPath, $Mode, $Port
    
    $frontendJob = Start-Job -ScriptBlock {
        param($scriptPath, $mode, $port)
        Set-Location (Split-Path $scriptPath)
        & $scriptPath -Frontend -Mode $mode -FrontendPort $port
    } -ArgumentList $PSCommandPath, $Mode, $FrontendPort
    
    Write-Success "Started backend server (Job ID: $($backendJob.Id))"
    Write-Success "Started frontend server (Job ID: $($frontendJob.Id))"
    
    Write-Info ""
    Write-Info "🚀 FISO Platform is starting up..."
    Write-Info "📊 Frontend: http://localhost:$FrontendPort"
    Write-Info "🔧 Backend API: http://localhost:$Port"
    Write-Info ""
    Write-Info "Press Ctrl+C to stop all services"
    Write-Info ""
    
    # Monitor jobs
    try {
        while ($true) {
            Start-Sleep -Seconds 2
            
            $backendState = Get-Job -Id $backendJob.Id | Select-Object -ExpandProperty State
            $frontendState = Get-Job -Id $frontendJob.Id | Select-Object -ExpandProperty State
            
            if ($backendState -eq 'Failed') {
                Write-Error "Backend server failed"
                Receive-Job -Id $backendJob.Id
                break
            }
            
            if ($frontendState -eq 'Failed') {
                Write-Error "Frontend server failed"
                Receive-Job -Id $frontendJob.Id
                break
            }
            
            if ($backendState -eq 'Completed' -or $frontendState -eq 'Completed') {
                Write-Warning "One of the servers completed unexpectedly"
                break
            }
        }
    } finally {
        Write-Info "Cleaning up background jobs..."
        Stop-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
        Stop-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
        Remove-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
        Remove-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
    }
}

# Main execution logic
try {
    # Pre-flight checks
    if (-not (Test-NodeJS)) { exit 1 }
    if (-not (Test-Python)) { exit 1 }
    
    # Install dependencies if needed
    if (-not (Install-Dependencies)) { exit 1 }
    
    # Determine what to start
    if ($Frontend -and -not $Backend) {
        Start-Frontend -FrontendPort $FrontendPort
    } elseif ($Backend -and -not $Frontend) {
        Start-Backend -BackendPort $Port
    } else {
        # Start both (default behavior)
        Start-FullStack
    }
    
} catch {
    Write-Error "An error occurred: $($_.Exception.Message)"
    exit 1
}