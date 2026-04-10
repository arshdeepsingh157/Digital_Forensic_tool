# AI-Powered Digital Forensics System - Quick Start

Write-Host "==================================================================" -ForegroundColor Cyan  
Write-Host "  Starting AI-Powered Digital Forensics System" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 3

Write-Host "[2/2] Starting Dashboard..." -ForegroundColor Yellow  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\python.exe -m streamlit run dashboard/app.py"

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "  ✅ System Started!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "`n📊 Dashboard:    http://localhost:8501" -ForegroundColor White
Write-Host "🔌 Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "📖 API Docs:     http://localhost:8000/api/docs`n" -ForegroundColor White
