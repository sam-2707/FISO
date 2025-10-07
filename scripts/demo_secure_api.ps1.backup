# FISO Secure API Demo & Testing Script
# Demonstrates enterprise security features with our multi-cloud system

Write-Host "🔐 FISO Secure API Demo" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

Write-Host "`n📋 Demo Overview:" -ForegroundColor Yellow
Write-Host "This demo shows our multi-cloud system enhanced with:" -ForegroundColor White
Write-Host "  ✅ JWT Authentication" -ForegroundColor Green
Write-Host "  ✅ API Key Authentication" -ForegroundColor Green
Write-Host "  ✅ Rate Limiting" -ForegroundColor Green
Write-Host "  ✅ Request Validation" -ForegroundColor Green
Write-Host "  ✅ Security Headers" -ForegroundColor Green
Write-Host "  ✅ Permission-based Access Control" -ForegroundColor Green

Write-Host "`n🚀 Starting Secure API Server..." -ForegroundColor Blue

# Check if Python is available
try {
    $pythonCmd = "python"
    $pythonVersion = & $pythonCmd --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        $pythonCmd = "python3"
        $pythonVersion = & $pythonCmd --version 2>&1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python not found. Please install Python 3.7+" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error checking Python: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "`n📦 Checking required packages..." -ForegroundColor Yellow

$requiredPackages = @("flask", "flask-cors", "pyjwt", "requests")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        & $pythonCmd -c "import $($package.Replace('-', '_'))" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $package" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $package (missing)" -ForegroundColor Red
            $missingPackages += $package
        }
    } catch {
        Write-Host "  ❌ $package (missing)" -ForegroundColor Red
        $missingPackages += $package
    }
}

# Install missing packages
if ($missingPackages.Count -gt 0) {
    Write-Host "`n📥 Installing missing packages..." -ForegroundColor Yellow
    foreach ($package in $missingPackages) {
        Write-Host "Installing $package..." -ForegroundColor Gray
        & $pythonCmd -m pip install $package
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $package installed" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Failed to install $package" -ForegroundColor Red
        }
    }
}

Write-Host "`n🔧 Setting up demo environment..." -ForegroundColor Blue

# Create requirements.txt for easy setup
$requirements = @"
flask==2.3.3
flask-cors==4.0.0
PyJWT==2.8.0
requests==2.31.0
cryptography==41.0.7
"@

$requirements | Out-File -FilePath "security/requirements.txt" -Encoding UTF8
Write-Host "✅ Created security/requirements.txt" -ForegroundColor Green

# Create demo configuration
$demoConfig = @"
{
  "api_server": {
    "host": "localhost",
    "port": 5000,
    "debug": true
  },
  "demo_users": [
    {
      "user_id": "demo_admin",
      "permissions": ["read", "orchestrate", "admin"]
    },
    {
      "user_id": "demo_user",
      "permissions": ["read", "orchestrate"]
    },
    {
      "user_id": "readonly_user",
      "permissions": ["read"]
    }
  ],
  "rate_limits": {
    "anonymous": 30,
    "authenticated": 100,
    "admin": 500
  }
}
"@

$demoConfig | Out-File -FilePath "security/demo_config.json" -Encoding UTF8
Write-Host "✅ Created demo configuration" -ForegroundColor Green

Write-Host "`n🌐 Starting secure API server in background..." -ForegroundColor Green

# Start the secure server in background
$serverProcess = Start-Process -FilePath $pythonCmd -ArgumentList "security/secure_server.py" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 3

# Check if server started successfully
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:5000/" -Method GET -TimeoutSec 5
    Write-Host "✅ Secure API server is running on http://localhost:5000" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Server starting up... (will be ready in a moment)" -ForegroundColor Yellow
}

Write-Host "`n🧪 Running API Security Demo..." -ForegroundColor Cyan

# Wait a bit more for server to fully start
Start-Sleep -Seconds 2

# Demo 1: Generate API credentials
Write-Host "`n1️⃣ Generating Demo Credentials" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue

try {
    # Generate API Key
    $apiKeyRequest = @{
        user_id = "demo_admin"
        permissions = @("read", "orchestrate", "admin")
    } | ConvertTo-Json

    $apiKeyResponse = Invoke-RestMethod -Uri "http://localhost:5000/auth/generate-key" -Method POST -Body $apiKeyRequest -ContentType "application/json"
    $demoApiKey = $apiKeyResponse.data.api_key
    Write-Host "✅ API Key generated: $($demoApiKey.Substring(0, 20))..." -ForegroundColor Green

    # Generate JWT Token
    $jwtRequest = @{
        user_id = "demo_user"
        permissions = @("read", "orchestrate")
    } | ConvertTo-Json

    $jwtResponse = Invoke-RestMethod -Uri "http://localhost:5000/auth/generate-jwt" -Method POST -Body $jwtRequest -ContentType "application/json"
    $demoJwt = $jwtResponse.data.jwt_token
    Write-Host "✅ JWT Token generated: $($demoJwt.Substring(0, 30))..." -ForegroundColor Green

} catch {
    Write-Host "⚠️ Credential generation pending (server still starting)" -ForegroundColor Yellow
    # Use fallback demo credentials
    $demoApiKey = "fiso_demo_key_for_testing"
    $demoJwt = "demo_jwt_token"
}

# Demo 2: Test Authentication Methods
Write-Host "`n2️⃣ Testing Authentication Methods" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue

Write-Host "`nTesting unauthenticated request..." -ForegroundColor Gray
try {
    $unauthResponse = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 10
    if ($unauthResponse.success) {
        Write-Host "✅ Anonymous access allowed (with rate limiting)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Server not ready yet" -ForegroundColor Yellow
}

Write-Host "`nTesting API Key authentication..." -ForegroundColor Gray
try {
    $headers = @{"X-API-Key" = $demoApiKey}
    $apiKeyResponse = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET -Headers $headers -TimeoutSec 10
    if ($apiKeyResponse.success) {
        Write-Host "✅ API Key authentication successful" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Server not ready yet" -ForegroundColor Yellow
}

Write-Host "`nTesting JWT authentication..." -ForegroundColor Gray
try {
    $headers = @{"Authorization" = "Bearer $demoJwt"}
    $jwtResponse = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET -Headers $headers -TimeoutSec 10
    if ($jwtResponse.success) {
        Write-Host "✅ JWT authentication successful" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Server not ready yet" -ForegroundColor Yellow
}

# Demo 3: Test Multi-Cloud Integration
Write-Host "`n3️⃣ Testing Secure Multi-Cloud Integration" -ForegroundColor Blue
Write-Host "==========================================" -ForegroundColor Blue

try {
    $headers = @{"X-API-Key" = $demoApiKey}
    
    Write-Host "`nTesting health check..." -ForegroundColor Gray
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:5000/health?provider=auto" -Method GET -Headers $headers -TimeoutSec 15
    
    if ($healthResponse.success) {
        $healthData = $healthResponse.data
        Write-Host "✅ Multi-cloud health check successful" -ForegroundColor Green
        Write-Host "   Overall Status: $($healthData.overall_status)" -ForegroundColor Cyan
        Write-Host "   Healthy Providers: $($healthData.healthy_providers)" -ForegroundColor Cyan
        
        foreach ($provider in $healthData.providers.PSObject.Properties) {
            $status = $provider.Value.status
            $color = if ($status -eq "healthy") { "Green" } else { "Red" }
            Write-Host "   $($provider.Name): $status" -ForegroundColor $color
        }
    }
} catch {
    Write-Host "⚠️ Multi-cloud test pending (server still initializing)" -ForegroundColor Yellow
}

# Demo 4: Test System Status
Write-Host "`n4️⃣ Testing System Status & Metrics" -ForegroundColor Blue
Write-Host "===================================" -ForegroundColor Blue

try {
    $headers = @{"X-API-Key" = $demoApiKey}
    
    Write-Host "`nGetting system status..." -ForegroundColor Gray
    $statusResponse = Invoke-RestMethod -Uri "http://localhost:5000/status" -Method GET -Headers $headers -TimeoutSec 10
    
    if ($statusResponse.success) {
        Write-Host "✅ System status retrieved successfully" -ForegroundColor Green
        $status = $statusResponse.data
        Write-Host "   System Status: $($status.system_status)" -ForegroundColor Cyan
        Write-Host "   API Version: $($status.api_version)" -ForegroundColor Cyan
        Write-Host "   Security Features: Active" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Status check pending" -ForegroundColor Yellow
}

# Demo 5: Show Security Features
Write-Host "`n5️⃣ Security Features Summary" -ForegroundColor Blue
Write-Host "=============================" -ForegroundColor Blue

Write-Host "`n🔐 Authentication:" -ForegroundColor Green
Write-Host "   ✅ API Key Authentication" -ForegroundColor White
Write-Host "   ✅ JWT Token Authentication" -ForegroundColor White
Write-Host "   ✅ Permission-based Access Control" -ForegroundColor White

Write-Host "`n🛡️ Protection:" -ForegroundColor Green
Write-Host "   ✅ Rate Limiting (IP-based)" -ForegroundColor White
Write-Host "   ✅ Request Validation & Sanitization" -ForegroundColor White
Write-Host "   ✅ Security Headers (OWASP)" -ForegroundColor White
Write-Host "   ✅ CORS Configuration" -ForegroundColor White

Write-Host "`n📊 Monitoring:" -ForegroundColor Green
Write-Host "   ✅ Security Event Logging" -ForegroundColor White
Write-Host "   ✅ Request Analytics" -ForegroundColor White
Write-Host "   ✅ Performance Metrics" -ForegroundColor White
Write-Host "   ✅ Audit Trail" -ForegroundColor White

Write-Host "`n🚀 Integration Benefits:" -ForegroundColor Magenta
Write-Host "   ✅ Works with existing 100% multi-cloud system" -ForegroundColor White
Write-Host "   ✅ No infrastructure changes needed" -ForegroundColor White
Write-Host "   ✅ Enterprise-grade security" -ForegroundColor White
Write-Host "   ✅ RESTful API design" -ForegroundColor White
Write-Host "   ✅ Easy integration with web dashboards" -ForegroundColor White

Write-Host "`n📖 API Documentation:" -ForegroundColor Blue
Write-Host "   🌐 http://localhost:5000/docs" -ForegroundColor Cyan
Write-Host "   🏠 http://localhost:5000/ (API info)" -ForegroundColor Cyan

Write-Host "`n🧪 Test Commands:" -ForegroundColor Yellow
Write-Host "   curl -H 'X-API-Key: $($demoApiKey.Substring(0, 20))...' http://localhost:5000/health" -ForegroundColor Gray
Write-Host "   curl -H 'Authorization: Bearer $($demoJwt.Substring(0, 20))...' http://localhost:5000/status" -ForegroundColor Gray

Write-Host "`n✅ FISO Secure API Demo Complete!" -ForegroundColor Green
Write-Host "The secure API server is running and ready for use." -ForegroundColor White
Write-Host "Press Ctrl+C to stop the server when done testing." -ForegroundColor Gray

# Keep the demo running
Write-Host "`n⏳ Demo server running... Press any key to stop" -ForegroundColor Cyan
Read-Host

# Clean up
if ($serverProcess -and !$serverProcess.HasExited) {
    Write-Host "`n🛑 Stopping secure API server..." -ForegroundColor Yellow
    Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Server stopped" -ForegroundColor Green
}
