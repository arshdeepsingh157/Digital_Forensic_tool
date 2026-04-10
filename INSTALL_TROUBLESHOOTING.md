# 🔧 Installation Troubleshooting Guide

This guide helps resolve common installation issues for the AI-Powered Digital Forensics System.

---

## ❌ Error: Network Connection Failed

**Error Message:**
```
[Errno 11001] getaddrinfo failed
HTTPSConnectionPool: Max retries exceeded
```

### Root Cause
Your system cannot reach Python's package repository (pypi.org). This is usually due to:
1. No internet connection
2. Firewall blocking pip
3. Proxy/VPN issues
4. DNS resolution problems

---

## 🔍 Troubleshooting Steps

### Step 1: Check Internet Connection

**Test your connection:**
```powershell
# Test basic connectivity
Test-Connection -ComputerName google.com -Count 2

# Test HTTPS connectivity
Invoke-WebRequest -Uri https://pypi.org -UseBasicParsing
```

**If these fail:**
- Check your network cable/WiFi connection
- Restart your router
- Contact your network administrator
- Try using a mobile hotspot temporarily

---

### Step 2: Configure Firewall/Antivirus

**Windows Firewall:**
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Python.exe from `.venv\Scripts\python.exe`
4. Allow both Private and Public networks

**Antivirus:**
- Temporarily disable antivirus to test
- If it works, add Python to whitelist
- Re-enable antivirus

---

### Step 3: Configure Proxy Settings (If Applicable)

**If you're behind a corporate proxy:**

```powershell
# Set proxy for pip (replace with your proxy address)
$env:HTTP_PROXY="http://proxy.company.com:8080"
$env:HTTPS_PROXY="http://proxy.company.com:8080"

# Or configure in pip.ini
# Create/edit: %APPDATA%\pip\pip.ini
[global]
proxy = http://proxy.company.com:8080
trusted-host = pypi.org
               files.pythonhosted.org
```

**Then retry installation:**
```powershell
python -m pip install -r requirements.txt
```

---

### Step 4: Use Alternative DNS

**Change DNS to Google's public DNS:**
1. Open Network Connections
2. Right-click your connection → Properties
3. Select "Internet Protocol Version 4 (TCP/IPv4)"
4. Use these DNS servers:
   - Preferred: `8.8.8.8`
   - Alternate: `8.8.4.4`
5. Click OK and restart your connection

---

### Step 5: Install Packages Individually

**If full installation fails, install one by one:**

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install packages one by one
python -m pip install fastapi==0.109.0
python -m pip install uvicorn==0.27.0
python -m pip install pydantic==2.5.3
python -m pip install pydantic-settings==2.1.0

# Database packages (these might be problematic)
python -m pip install psycopg2-binary==2.9.9
python -m pip install pymongo==4.6.1
python -m pip install sqlalchemy==2.0.25

# If psycopg2-binary fails, try psycopg2
python -m pip install psycopg2

# Continue with remaining packages...
```

---

### Step 6: Use Minimal Installation

**Install only essential packages first:**

```powershell
python -m pip install -r requirements-minimal.txt
```

This installs core FastAPI components. Add other packages later when connection is stable.

---

### Step 7: Offline Installation (Advanced)

**If you have no internet but have another computer:**

1. **On a computer WITH internet:**
   ```powershell
   # Download all packages
   pip download -r requirements.txt -d packages/
   ```

2. **Transfer the `packages/` folder to your offline computer**

3. **On offline computer:**
   ```powershell
   python -m pip install --no-index --find-links=packages/ -r requirements.txt
   ```

---

### Step 8: Use Conda (Alternative)

**If pip continues to fail, try Anaconda:**

```powershell
# Install Anaconda from https://www.anaconda.com/download

# Create conda environment
conda create -n forensics python=3.9
conda activate forensics

# Install packages with conda
conda install fastapi uvicorn pandas numpy opencv
conda install -c conda-forge pillow exifread

# Install remaining with pip
pip install pydantic-settings loguru
```

---

## 🚨 Common Package-Specific Issues

### psycopg2-binary Installation Fails

**Error:** Cannot compile or download psycopg2-binary

**Solutions:**

**Option 1: Use precompiled wheel**
```powershell
python -m pip install psycopg2-binary --only-binary :all:
```

**Option 2: Install PostgreSQL first**
1. Download PostgreSQL from https://www.postgresql.org/download/
2. Install it (adds required libraries)
3. Retry: `pip install psycopg2-binary`

**Option 3: Use psycopg (newer version)**
```powershell
python -m pip install psycopg[binary]
```

---

### OpenCV Installation Issues

**Error:** opencv-python fails to install

**Solutions:**

**Option 1: Install specific version**
```powershell
python -m pip install opencv-python-headless
```

**Option 2: Use conda**
```powershell
conda install opencv
```

---

### NumPy/Pandas Wheel Issues

**Error:** Cannot find compatible wheel

**Solutions:**

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install numpy first
python -m pip install numpy

# Then pandas
python -m pip install pandas
```

---

## ✅ Verification Steps

**After installation, verify packages:**

```powershell
# Check installed packages
python -m pip list

# Test imports
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import pandas; print('Pandas:', pandas.__version__)"
```

---

## 🎯 Quick Fix Script

**Run this automated troubleshooting script:**

```powershell
.\install_packages.ps1
```

This script:
- Retries installation multiple times
- Uses increased timeout
- Provides detailed error messages
- Suggests next steps

---

## 📞 Still Having Issues?

### Check System Requirements
- ✅ Python 3.9 or higher
- ✅ 64-bit Python (not 32-bit)
- ✅ Administrator privileges (for some packages)
- ✅ 2GB+ free disk space

### Get More Help

**Check logs:**
```powershell
python -m pip install -r requirements.txt --verbose > install_log.txt 2>&1
```

**System information:**
```powershell
python --version
python -m pip --version
systeminfo | Select-String "OS Name","OS Version"
```

**Contact support with:**
1. Error messages from install_log.txt
2. Python version
3. Windows version
4. Network setup (proxy/firewall info)

---

## 🔄 Alternative: Docker Installation

**If all else fails, use Docker:**

```dockerfile
# Create Dockerfile in project root
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```powershell
# Build and run
docker build -t forensics-system .
docker run -p 8000:8000 forensics-system
```

---

## 📝 Post-Installation Checklist

Once packages install successfully:

- [ ] All packages show in `pip list`
- [ ] Can import fastapi: `python -c "import fastapi"`
- [ ] Can import sqlalchemy: `python -c "import sqlalchemy"`
- [ ] Can import cv2: `python -c "import cv2"`
- [ ] No error messages
- [ ] Ready to configure .env file

**Next steps:**
1. Copy `.env.example` to `.env`
2. Configure database settings
3. Run `python scripts\init_db.py`
4. Start the system with `.\start.ps1`

---

**Good luck! Your forensics system will be running soon! 🚀**
