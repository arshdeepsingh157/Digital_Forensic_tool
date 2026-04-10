# Package Installation Helper Script
# Run this after internet connection is restored

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  AI-Powered Digital Forensics System - Package Installer" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# Activate virtual environment
Write-Host "`n[1/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "`n[2/4] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Try installing with increased timeout and retries
Write-Host "`n[3/4] Installing packages (with retry logic)..." -ForegroundColor Yellow
$retries = 3
$installed = $false

for ($i = 1; $i -le $retries; $i++) {
    Write-Host "  Attempt $i of $retries..." -ForegroundColor Gray
    
    try {
        python -m pip install -r requirements.txt --timeout 120 --retries 5
        $installed = $true
        break
    }
    catch {
        Write-Host "  Attempt $i failed. Retrying..." -ForegroundColor Red
        Start-Sleep -Seconds 2
    }
}

if ($installed) {
    Write-Host "`n[4/4] Installation successful!" -ForegroundColor Green
    Write-Host "`n==================================================================" -ForegroundColor Cyan
    Write-Host "  All packages installed successfully!" -ForegroundColor Green
    Write-Host "==================================================================" -ForegroundColor Cyan
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. Configure .env file with your database settings"
    Write-Host "  2. Run: python scripts\init_db.py"
    Write-Host "  3. Start the system with: .\start.ps1"
}
else {
    Write-Host "`n[4/4] Installation failed after $retries attempts" -ForegroundColor Red
    Write-Host "`nTroubleshooting steps:" -ForegroundColor Yellow
    Write-Host "  1. Check your internet connection"
    Write-Host "  2. If behind a proxy, configure pip proxy settings"
    Write-Host "  3. Try installing packages individually"
    Write-Host "  4. Contact your network administrator"
}
