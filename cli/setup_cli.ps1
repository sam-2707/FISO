# FISO CLI Setup Script
# This script installs the FISO CLI for easy access

Write-Host "Setting up FISO CLI..." -ForegroundColor Cyan
Write-Host ""

# Get the current directory (should be the FISO root)
$FISORoot = Get-Location
$CLIPath = Join-Path $FISORoot "cli"
$FISOCmd = Join-Path $CLIPath "fiso.cmd"
$FISOPy = Join-Path $CLIPath "fiso.py"

# Verify files exist
if (-not (Test-Path $FISOCmd)) {
    Write-Host "Error: fiso.cmd not found at $FISOCmd" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $FISOPy)) {
    Write-Host "Error: fiso.py not found at $FISOPy" -ForegroundColor Red
    exit 1
}

# Check if Python environment exists
$PythonPath = Join-Path $FISORoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) {
    Write-Host "Error: Python virtual environment not found" -ForegroundColor Red
    Write-Host "Please run the Python environment setup first" -ForegroundColor Yellow
    exit 1
}

Write-Host "All CLI files found" -ForegroundColor Green

# Install required packages
Write-Host "Installing CLI dependencies..." -ForegroundColor Yellow
& $PythonPath -m pip install requests argparse pathlib --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "Warning: Some dependencies may not have installed correctly" -ForegroundColor Yellow
}

# Add to PATH (optional)
$CurrentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($CurrentPath -notlike "*$CLIPath*") {
    Write-Host ""
    Write-Host "CLI Installation Options:" -ForegroundColor Cyan
    Write-Host "1. Add to PATH (recommended) - Run 'fiso' from anywhere"
    Write-Host "2. Use directly - Run from current directory only"
    Write-Host ""
    
    $choice = Read-Host "Add FISO CLI to your PATH? (y/n)"
    
    if ($choice -eq "y" -or $choice -eq "Y") {
        try {
            $NewPath = "$CurrentPath;$CLIPath"
            [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
            Write-Host "FISO CLI added to PATH" -ForegroundColor Green
            Write-Host "You may need to restart your terminal for PATH changes to take effect" -ForegroundColor Yellow
        } catch {
            Write-Host "Failed to add to PATH: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "You can manually add '$CLIPath' to your PATH" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "FISO CLI Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Getting Started:" -ForegroundColor Cyan
Write-Host "1. First, authenticate with your FISO API:"
Write-Host "   fiso auth login" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Check system status:"
Write-Host "   fiso status" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Monitor in real-time:"
Write-Host "   fiso watch" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Get help anytime:"
Write-Host "   fiso --help" -ForegroundColor Yellow
Write-Host ""

# Test the CLI
Write-Host "Testing CLI installation..." -ForegroundColor Cyan
try {
    $TestOutput = & $FISOCmd --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "CLI test successful!" -ForegroundColor Green
    } else {
        Write-Host "CLI test completed with warnings" -ForegroundColor Yellow
    }
} catch {
    Write-Host "CLI test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Quick Links:" -ForegroundColor Cyan
Write-Host "   Dashboard: http://localhost:8080/secure_dashboard.html"
Write-Host "   API Docs:  http://localhost:5000/docs"
Write-Host "   CLI Help:  fiso --help"
Write-Host ""
Write-Host "Happy orchestrating!" -ForegroundColor Green
