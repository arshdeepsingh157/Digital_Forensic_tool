# AI-Powered Digital Forensics System - Quick Start Script
# This script helps you quickly start all services

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "AI-Powered Digital Forensics System" -ForegroundColor Cyan
Write-Host "Quick Start Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Red
    Write-Host "Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env file with your configuration before continuing." -ForegroundColor Yellow
    Write-Host "Press any key to continue after editing .env..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Install dependencies if needed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
pip install -q --upgrade pip

# Start services
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Starting Services" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "What would you like to start?
[1] FastAPI Backend only
[2] Streamlit Dashboard only
[3] Both Backend and Dashboard
[4] Initialize Database
[Q] Quit

Enter your choice"

switch ($choice) {
    "1" {
        Write-Host "Starting FastAPI Backend..." -ForegroundColor Green
        Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
        uvicorn backend.main:app --reload --port 8000
    }
    "2" {
        Write-Host "Starting Streamlit Dashboard..." -ForegroundColor Green
        Write-Host "Dashboard will be available at: http://localhost:8501" -ForegroundColor Cyan
        streamlit run dashboard/app.py
    }
    "3" {
        Write-Host "Starting both services..." -ForegroundColor Green
        Write-Host ""
        Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Dashboard: http://localhost:8501" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Opening new terminal for Backend..." -ForegroundColor Yellow
        
        # Start backend in new window
        Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "& {
            cd '$PWD'
            & venv\Scripts\Activate.ps1
            Write-Host 'Starting FastAPI Backend...' -ForegroundColor Green
            uvicorn backend.main:app --reload --port 8000
        }"
        
        Start-Sleep -Seconds 2
        
        # Start dashboard in current window
        Write-Host "Starting Streamlit Dashboard..." -ForegroundColor Green
        streamlit run dashboard/app.py
    }
    "4" {
        Write-Host "Initializing database..." -ForegroundColor Green
        python scripts/init_db.py
        Write-Host ""
        Write-Host "Database initialization complete!" -ForegroundColor Green
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    "Q" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
        exit
    }
}
