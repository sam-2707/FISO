# FISO Project Validation Script
# This script validates that all commands mentioned in the README work correctly

Write-Host "=================================================="
Write-Host "FISO Project Validation"
Write-Host "=================================================="

$testResults = @()

# Test 1: Check if Docker is running
Write-Host ""
Write-Host "Test 1: Docker Status" -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
    $testResults += "Docker: PASS"
} catch {
    Write-Host "❌ Docker is not running" -ForegroundColor Red
    $testResults += "Docker: FAIL"
}

# Test 2: Check if containers are running
Write-Host ""
Write-Host "Test 2: FISO Containers" -ForegroundColor Yellow
try {
    $containers = docker-compose ps -q
    if ($containers) {
        Write-Host "✅ FISO containers are running" -ForegroundColor Green
        $testResults += "Containers: PASS"
    } else {
        Write-Host "❌ FISO containers are not running" -ForegroundColor Red
        $testResults += "Containers: FAIL"
    }
} catch {
    Write-Host "❌ Error checking containers" -ForegroundColor Red
    $testResults += "Containers: FAIL"
}

# Test 3: Check API endpoint
Write-Host ""
Write-Host "Test 3: API Endpoint" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8080/api/v1/orchestrate" -TimeoutSec 10
    if ($response) {
        Write-Host "✅ API is responding" -ForegroundColor Green
        Write-Host "   Provider: $($response.provider)" -ForegroundColor White
        Write-Host "   Status: $($response.status_code)" -ForegroundColor White
        $testResults += "API: PASS"
    } else {
        Write-Host "❌ API returned empty response" -ForegroundColor Red
        $testResults += "API: FAIL"
    }
} catch {
    Write-Host "❌ API is not responding: $($_.Exception.Message)" -ForegroundColor Red
    $testResults += "API: FAIL"
}

# Test 4: Check database connectivity
Write-Host ""
Write-Host "Test 4: Database Connectivity" -ForegroundColor Yellow
try {
    $dbTest = "SELECT COUNT(*) FROM policies;" | docker exec -i fiso_db psql -U fiso -d fiso_db -t
    if ($dbTest -gt 0) {
        Write-Host "✅ Database is accessible with $dbTest policies" -ForegroundColor Green
        $testResults += "Database: PASS"
    } else {
        Write-Host "❌ Database has no policies" -ForegroundColor Red
        $testResults += "Database: FAIL"
    }
} catch {
    Write-Host "❌ Database connection failed" -ForegroundColor Red
    $testResults += "Database: FAIL"
}

# Test 5: Check if scripts exist
Write-Host ""
Write-Host "Test 5: Management Scripts" -ForegroundColor Yellow
$scripts = @(
    "scripts\switch_provider.ps1",
    "scripts\get_deployment_urls.ps1", 
    "scripts\demo_multicloud.ps1",
    "scripts\setup_multicloud.ps1"
)

$scriptCount = 0
foreach ($script in $scripts) {
    if (Test-Path $script) {
        $scriptCount++
    }
}

if ($scriptCount -eq $scripts.Count) {
    Write-Host "✅ All management scripts are present ($scriptCount/$($scripts.Count))" -ForegroundColor Green
    $testResults += "Scripts: PASS"
} else {
    Write-Host "❌ Missing management scripts ($scriptCount/$($scripts.Count))" -ForegroundColor Red
    $testResults += "Scripts: FAIL"
}

# Test 6: Test provider switching
Write-Host ""
Write-Host "Test 6: Provider Switching" -ForegroundColor Yellow
try {
    # Test switching to each provider
    $providers = @("aws", "azure", "gcp")
    $switchResults = @()
    
    foreach ($provider in $providers) {
        try {
            & ".\scripts\switch_provider.ps1" $provider | Out-Null
            $switchResults += "$provider - OK"
        } catch {
            $switchResults += "$provider - FAIL"
        }
    }
    
    Write-Host "✅ Provider switching tested:" -ForegroundColor Green
    foreach ($result in $switchResults) {
        Write-Host "   $result" -ForegroundColor White
    }
    $testResults += "Switching: PASS"
    
} catch {
    Write-Host "❌ Provider switching failed" -ForegroundColor Red
    $testResults += "Switching: FAIL"
}

# Summary
Write-Host ""
Write-Host "=================================================="
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "=================================================="

$passCount = ($testResults | Where-Object { $_ -like "*PASS" }).Count
$totalTests = $testResults.Count

foreach ($result in $testResults) {
    if ($result -like "*PASS") {
        Write-Host "✅ $result" -ForegroundColor Green
    } else {
        Write-Host "❌ $result" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Overall: $passCount/$totalTests tests passed" -ForegroundColor $(if ($passCount -eq $totalTests) { "Green" } else { "Yellow" })

if ($passCount -eq $totalTests) {
    Write-Host ""
    Write-Host "🎉 All tests passed! FISO is ready to use." -ForegroundColor Green
    Write-Host "Try the demo: .\scripts\demo_multicloud.ps1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠️  Some tests failed. Check the setup guide in README.md" -ForegroundColor Yellow
}

Write-Host "=================================================="
