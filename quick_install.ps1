# Quick Install - Essential Packages Only
# Skip complex packages for now

Write-Host "Installing essential packages..." -ForegroundColor Cyan

python -m pip install --upgrade pip

# Core packages (use latest compatible versions)
python -m pip install `
    fastapi `
    "uvicorn[standard]" `
    pydantic `
    pydantic-settings `
    python-multipart `
    python-dotenv `
    loguru `
    sqlalchemy `
    pymongo `
    pandas `
    numpy `
    Pillow `
    opencv-python `
    exifread `
    streamlit `
    plotly

Write-Host "`nVerifying installation..." -ForegroundColor Yellow
python -m pip list | Select-String "fastapi|uvicorn|pydantic|sqlalchemy|pymongo|opencv|streamlit|plotly|Pillow|pandas|numpy"

Write-Host "`nDone! You can now start the application." -ForegroundColor Green
