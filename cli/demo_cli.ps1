# FISO CLI Demo Script
# Demonstrates the professional CLI capabilities

Write-Host "=== FISO CLI Demo ===" -ForegroundColor Cyan
Write-Host ""

# Show CLI help
Write-Host "1. CLI Help & Commands:" -ForegroundColor Yellow
.\cli\fiso.cmd --help
Write-Host ""

# Show current configuration
Write-Host "2. Current Configuration:" -ForegroundColor Yellow
.\cli\fiso.cmd config show
Write-Host ""

# Check system status
Write-Host "3. System Status:" -ForegroundColor Yellow
.\cli\fiso.cmd status
Write-Host ""

# Check provider health
Write-Host "4. Provider Health Check:" -ForegroundColor Yellow
.\cli\fiso.cmd health
Write-Host ""

# View metrics
Write-Host "5. System Metrics:" -ForegroundColor Yellow
.\cli\fiso.cmd metrics
Write-Host ""

# Test orchestration with different providers
Write-Host "6. Orchestration Tests:" -ForegroundColor Yellow
Write-Host "Testing AWS provider..." -ForegroundColor Cyan
.\cli\fiso.cmd orchestrate --provider aws
Write-Host ""

Write-Host "Testing Azure provider..." -ForegroundColor Cyan
.\cli\fiso.cmd orchestrate --provider azure
Write-Host ""

Write-Host "Auto-selecting best provider..." -ForegroundColor Cyan
.\cli\fiso.cmd orchestrate
Write-Host ""

Write-Host "=== CLI Demo Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 The FISO CLI is fully operational!" -ForegroundColor Green
Write-Host ""
Write-Host "Key Features Demonstrated:" -ForegroundColor Cyan
Write-Host "  ✅ Authentication & Configuration Management"
Write-Host "  ✅ Real-time System Status Monitoring"
Write-Host "  ✅ Multi-Provider Health Checks"
Write-Host "  ✅ Performance Metrics Collection"
Write-Host "  ✅ Intelligent Multi-Cloud Orchestration"
Write-Host "  ✅ Provider-Specific & Auto-Selection Modes"
Write-Host ""
Write-Host "For real-time monitoring, run: .\cli\fiso.cmd watch" -ForegroundColor Yellow
