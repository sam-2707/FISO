# FISO Production Server Startup Script for Windows
# Starts the complete production backend with all services

Write-Host "🔥 FISO Production Server Startup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if we're in the correct directory
$currentDir = Get-Location
$backendPath = Join-Path $currentDir "backend"

if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Backend directory not found. Please run from the FISO root directory." -ForegroundColor Red
    exit 1
}

# Change to backend directory
Set-Location $backendPath

# Check Python installation
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
$venvPath = "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "❌ Virtual environment activation script not found" -ForegroundColor Red
    exit 1
}

# Install/upgrade requirements
Write-Host "📦 Installing production requirements..." -ForegroundColor Yellow
if (Test-Path "requirements-production.txt") {
    pip install -r requirements-production.txt --upgrade
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Some packages failed to install, but continuing..." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ requirements-production.txt not found, installing basic packages..." -ForegroundColor Yellow
    pip install flask flask-cors pandas numpy scikit-learn requests
}

# Create necessary directories
Write-Host "📁 Setting up directories..." -ForegroundColor Yellow
$directories = @("logs", "data", "models")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✅ Created $dir directory" -ForegroundColor Green
    }
}

# Check if production server file exists
if (-not (Test-Path "start_production.py")) {
    Write-Host "❌ start_production.py not found" -ForegroundColor Red
    exit 1
}

# Start the production server
Write-Host "🚀 Starting FISO Production Server..." -ForegroundColor Green
Write-Host "   - API will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   - Health check: http://localhost:5000/api/production/health" -ForegroundColor Cyan
Write-Host "   - Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:FLASK_ENV = "production"
$env:PYTHONPATH = $backendPath

# Start server with error handling
try {
    python start_production.py
} catch {
    Write-Host "❌ Server startup failed: $_" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup
    Write-Host "🔄 Cleaning up..." -ForegroundColor Yellow
    Set-Location $currentDir
}

Write-Host "👋 FISO Production Server stopped" -ForegroundColor Cyan