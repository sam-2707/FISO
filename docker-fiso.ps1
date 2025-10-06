param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('build', 'run', 'stop', 'logs', 'clean', 'status')]
    [string]$Action,
    
    [Parameter()]
    [ValidateSet('dev', 'prod')]
    [string]$Mode = 'prod',
    
    [Parameter()]
    [int]$Port = 5000,
    
    [Parameter()]
    [string]$Profile = "",
    
    [Parameter()]
    [switch]$Simple
)

function Write-Info($message) {
    Write-Host "INFO: $message" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "SUCCESS: $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "ERROR: $message" -ForegroundColor Red
}

function Write-Warning($message) {
    Write-Host "WARNING: $message" -ForegroundColor Yellow
}

function Test-Docker {
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Success "Docker found: $dockerVersion"
            docker info >$null 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Docker daemon is running"
                return $true
            } else {
                Write-Error "Docker daemon is not running. Please start Docker Desktop."
                return $false
            }
        }
    } catch {
        Write-Error "Docker not found. Please install Docker Desktop."
        return $false
    }
    return $false
}

function Build-FisoContainer {
    if ($Simple) {
        Write-Info "Building FISO simple container (minimal dependencies)..."
        $dockerFile = "Dockerfile.simple"
        $reqFile = "requirements-minimal.txt"
        $imageName = "fiso:simple"
    } else {
        Write-Info "Building FISO production container..."
        $dockerFile = "Dockerfile.production"
        $reqFile = "requirements-production.txt"
        $imageName = "fiso:latest"
    }
    Write-Info "This may take several minutes for the first build..."
    
    # Check if requirements file exists and show its content
    if (Test-Path $reqFile) {
        $reqContent = Get-Content $reqFile -Raw
        if ($reqContent.Trim()) {
            Write-Info "Using $reqFile with content:"
            Write-Host $reqContent -ForegroundColor Gray
        } else {
            Write-Warning "$reqFile exists but is empty"
        }
    } else {
        Write-Warning "$reqFile not found"
    }
    
    # Build with progress output
    docker build -f $dockerFile -t $imageName . --progress=plain
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container built successfully!"
        Write-Info "Image details:"
        docker images $imageName --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
        
        # Test the container briefly
        Write-Info "Testing container startup..."
        $testResult = docker run --rm $imageName python -c "print('Container test successful')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Container test passed: $testResult"
        } else {
            Write-Warning "Container test failed: $testResult"
        }
    } else {
        Write-Error "Container build failed!"
        Write-Info "You can check detailed build logs in Docker Desktop"
        Write-Info "Common issues:"
        Write-Info "  - Network connectivity problems"
        Write-Info "  - Package version conflicts"
        Write-Info "  - Insufficient disk space"
        exit 1
    }
}

function Run-FisoContainer {
    $imageName = if ($Simple) { "fiso:simple" } else { "fiso:latest" }
    Write-Info "Starting FISO platform using $imageName..."
    docker stop fiso-container 2>$null
    docker rm fiso-container 2>$null
    
    docker run -d --name fiso-container -p "${Port}:5000" -p "5001:5001" $imageName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "FISO container started successfully!"
        Write-Info "Access FISO at: http://localhost:$Port"
        Write-Info "Real-time API at: http://localhost:5001"
    } else {
        Write-Error "Failed to start container"
        exit 1
    }
}

function Stop-FisoContainer {
    Write-Info "Stopping FISO services..."
    docker stop fiso-container 2>$null
    docker rm fiso-container 2>$null
    Write-Success "FISO services stopped"
}

function Show-FisoLogs {
    Write-Info "Showing logs from container..."
    docker logs -f fiso-container
}

function Show-FisoStatus {
    Write-Info "FISO Container Status:"
    docker ps -a --filter name=fiso-container
    Write-Host ""
    Write-Info "FISO Images:"
    docker images fiso
}

function Clean-FisoContainers {
    Write-Info "Cleaning up FISO containers and images..."
    docker stop fiso-container 2>$null
    docker rm fiso-container 2>$null
    docker rmi fiso:latest 2>$null
    docker image prune -f
    Write-Success "Cleanup completed"
}

Write-Info "FISO Docker Management Script"
Write-Info "============================="

if (-not (Test-Docker)) {
    exit 1
}

switch ($Action) {
    "build" { Build-FisoContainer }
    "run" { Run-FisoContainer }
    "stop" { Stop-FisoContainer }
    "logs" { Show-FisoLogs }
    "status" { Show-FisoStatus }
    "clean" { Clean-FisoContainers }
}

Write-Info "Operation completed."
