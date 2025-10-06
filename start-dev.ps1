# FISO Development Environment Launcher
# Starts both frontend and production backend for development

Write-Host "🚀 FISO Development Environment" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Check if we're in the correct directory
$currentDir = Get-Location
$frontendPath = Join-Path $currentDir "frontend"
$backendPath = Join-Path $currentDir "backend"

if (-not (Test-Path $frontendPath) -or -not (Test-Path $backendPath)) {
    Write-Host "❌ Frontend or backend directory not found. Please run from the FISO root directory." -ForegroundColor Red
    exit 1
}

# Function to start backend in background
function Start-Backend {
    Write-Host "🔧 Starting production backend..." -ForegroundColor Yellow
    
    Set-Location $backendPath
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path "venv")) {
        Write-Host "📦 Creating backend virtual environment..." -ForegroundColor Yellow
        python -m venv venv
    }
    
    # Activate virtual environment and start server
    $job = Start-Job -ScriptBlock {
        param($backendPath)
        Set-Location $backendPath
        & "venv\Scripts\Activate.ps1"
        $env:FLASK_ENV = "development"
        python start_production.py
    } -ArgumentList $backendPath
    
    Set-Location $currentDir
    return $job
}

# Function to start frontend
function Start-Frontend {
    Write-Host "⚛️ Starting React frontend..." -ForegroundColor Yellow
    
    Set-Location $frontendPath
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
            return $null
        }
    }
    
    # Start React development server
    Write-Host "🌐 Starting React development server..." -ForegroundColor Green
    npm start
    
    Set-Location $currentDir
}

# Start backend in background
Write-Host "🔄 Starting services..." -ForegroundColor Cyan
$backendJob = Start-Backend

if ($backendJob) {
    Write-Host "✅ Backend job started (ID: $($backendJob.Id))" -ForegroundColor Green
    
    # Wait a moment for backend to start
    Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Check if backend is responding
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/production/health" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend is healthy and ready" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Backend responded but may not be fully ready" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Backend health check failed, but continuing..." -ForegroundColor Yellow
    }
    
    # Start frontend (this will block until frontend is stopped)
    Write-Host ""
    Write-Host "🎯 Development Environment Ready!" -ForegroundColor Green
    Write-Host "   - Backend API: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "   - Frontend App: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "   - Press Ctrl+C in the frontend window to stop both services" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        Start-Frontend
    } finally {
        # Clean up background job when frontend stops
        Write-Host "🔄 Stopping backend service..." -ForegroundColor Yellow
        Stop-Job $backendJob
        Remove-Job $backendJob
        Write-Host "✅ Development environment stopped" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Failed to start backend service" -ForegroundColor Red
    exit 1
}

Write-Host "👋 FISO Development Environment stopped" -ForegroundColor Cyan