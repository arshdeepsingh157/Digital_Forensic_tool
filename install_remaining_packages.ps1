# Install Remaining Packages Script
# This script installs packages in groups to handle dependencies properly

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Installing Remaining Packages" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# Ensure virtual environment is activated
Write-Host "`n[Step 1] Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Install packages in groups
Write-Host "`n[Step 2] Installing image processing packages..." -ForegroundColor Yellow
python -m pip install Pillow==10.2.0 exifread==3.0.0 piexif==1.1.3

Write-Host "`n[Step 3] Installing OpenCV (this may take a moment)..." -ForegroundColor Yellow
python -m pip install opencv-python==4.9.0.80

Write-Host "`n[Step 4] Installing scientific packages..." -ForegroundColor Yellow
python -m pip install scikit-image==0.22.0 scikit-learn==1.4.0

Write-Host "`n[Step 5] Installing MongoDB driver..." -ForegroundColor Yellow
python -m pip install pymongo==4.6.1

Write-Host "`n[Step 6] Installing SQLAlchemy..." -ForegroundColor Yellow
python -m pip install sqlalchemy==2.0.25

Write-Host "`n[Step 7] Installing Streamlit..." -ForegroundColor Yellow
python -m pip install streamlit==1.30.0 plotly==5.18.0

Write-Host "`n[Step 8] Verifying installation..." -ForegroundColor Yellow
Write-Host "`nInstalled packages:" -ForegroundColor Cyan
python -m pip list | Select-String "fastapi|uvicorn|pydantic|sqlalchemy|opencv|pandas|streamlit|plotly|pymongo|Pillow|scikit"

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Copy .env.example to .env and configure"
Write-Host "  2. Run: python scripts\init_db.py"
Write-Host "  3. Start: .\start.ps1"
