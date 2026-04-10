# ✅ Setup Verification Checklist

Use this checklist to verify your AI-Powered Digital Forensics System is properly configured.

---

## 📋 Pre-Installation Checklist

### System Requirements
- [ ] Python 3.9 or higher installed
- [ ] PostgreSQL 13+ installed and running
- [ ] MongoDB 4.4+ installed (optional but recommended)
- [ ] At least 2GB free disk space
- [ ] Internet connection for package downloads

### Verify Installations
```bash
# Check Python version
python --version  # Should be 3.9+

# Check PostgreSQL
psql --version    # Should be 13+

# Check MongoDB (if using)
mongod --version  # Should be 4.4+
```

---

## 📦 Installation Checklist

### 1. Project Setup
- [ ] Cloned/downloaded repository
- [ ] Navigated to project directory
- [ ] Created virtual environment (`python -m venv venv`)
- [ ] Activated virtual environment
  - Windows: `venv\Scripts\activate`
  - Linux/Mac: `source venv/bin/activate`

### 2. Dependencies
- [ ] Upgraded pip: `pip install --upgrade pip`
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] No error messages during installation

### 3. Database Configuration

#### PostgreSQL
- [ ] PostgreSQL service is running
- [ ] Created database: `forensic_db`
- [ ] Created user: `forensic_user`
- [ ] Granted privileges to user
- [ ] Can connect: `psql -U forensic_user -d forensic_db`

#### MongoDB (Optional)
- [ ] MongoDB service is running
- [ ] Can connect: `mongo` or `mongosh`

---

## 🔧 Configuration Checklist

### Environment Variables
- [ ] Copied `.env.example` to `.env`
- [ ] Updated PostgreSQL credentials in `.env`
- [ ] Updated MongoDB URI in `.env` (if using)
- [ ] Generated and set SECRET_KEY
- [ ] Reviewed all configuration values

### Key `.env` Settings to Verify
```env
# PostgreSQL - UPDATE THESE
POSTGRES_USER=forensic_user          ✅ Verified
POSTGRES_PASSWORD=your_password      ✅ Updated
POSTGRES_DB=forensic_db             ✅ Verified
POSTGRES_HOST=localhost             ✅ Verified
POSTGRES_PORT=5432                  ✅ Verified

# MongoDB - UPDATE IF USING
MONGO_URI=mongodb://localhost:27017/ ✅ Verified
MONGO_DB=forensic_logs              ✅ Verified

# API Configuration
API_PORT=8000                       ✅ Default OK
SECRET_KEY=<generated>              ✅ Generated

# Storage
STORAGE_PATH=./storage              ✅ Default OK
MAX_FILE_SIZE=52428800              ✅ Default OK
```

---

## 🗄️ Database Initialization Checklist

### Run Initialization Script
- [ ] Executed: `python scripts/init_db.py`
- [ ] See "PostgreSQL connection successful" message
- [ ] See "MongoDB connection successful" message (if using)
- [ ] See "Database tables created successfully" message
- [ ] No error messages

### Verify Database Tables

**PostgreSQL:**
```sql
-- Connect to database
psql -U forensic_user -d forensic_db

-- List tables (should see 4 tables)
\dt

-- Expected tables:
-- forensic_files
-- processing_logs
-- integrity_checks
-- system_metrics
```

- [ ] `forensic_files` table exists
- [ ] `processing_logs` table exists
- [ ] `integrity_checks` table exists
- [ ] `system_metrics` table exists

---

## 🚀 Application Startup Checklist

### Backend (FastAPI)

**Start Command:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Verify:**
- [ ] Command executed without errors
- [ ] See "Uvicorn running on http://127.0.0.1:8000"
- [ ] See "Application startup complete"
- [ ] No database connection errors

**Test Endpoints:**
- [ ] Health check: http://localhost:8000/health
  - Should return: `{"status": "healthy"}`
- [ ] API docs: http://localhost:8000/api/docs
  - Should display Swagger UI
- [ ] Welcome: http://localhost:8000/
  - Should return welcome message

### Dashboard (Streamlit)

**Start Command:**
```bash
streamlit run dashboard/app.py
```

**Verify:**
- [ ] Command executed without errors
- [ ] See "You can now view your Streamlit app"
- [ ] See "Local URL: http://localhost:8501"
- [ ] Browser opens automatically (or navigate manually)

**Test Dashboard:**
- [ ] Dashboard page loads
- [ ] Sidebar navigation visible
- [ ] All 5 pages accessible:
  - [ ] 📊 Dashboard
  - [ ] ⬆️ Upload & Analyze
  - [ ] 📝 Reports
  - [ ] 📜 History
  - [ ] ✅ Integrity Checker

---

## 🧪 Functional Testing Checklist

### Test 1: File Upload via Dashboard
- [ ] Navigate to "Upload & Analyze" page
- [ ] Upload a test image (JPG/PNG)
- [ ] Analysis completes without errors
- [ ] Results display correctly:
  - [ ] Verdict shown
  - [ ] Overall score shown
  - [ ] Component scores visible
  - [ ] Recommendations listed
- [ ] File ID displayed

### Test 2: File Upload via API
- [ ] Open API docs: http://localhost:8000/api/docs
- [ ] Navigate to POST `/api/v1/upload`
- [ ] Click "Try it out"
- [ ] Upload test file
- [ ] Execute request
- [ ] Response shows:
  - [ ] `success: true`
  - [ ] `file_id` present
  - [ ] `overall_score` present
  - [ ] `verdict` present

### Test 3: View Dashboard Analytics
- [ ] Navigate to Dashboard page
- [ ] KPI cards display:
  - [ ] Total files count
  - [ ] Authentic count
  - [ ] Suspicious count
  - [ ] Tampered count
- [ ] Visualizations render:
  - [ ] Pie chart (verdict distribution)
  - [ ] Bar chart (score distribution)
  - [ ] Line chart (temporal trends)

### Test 4: Generate Report
- [ ] Navigate to Reports page
- [ ] Enter file ID from previous test
- [ ] Click "Generate Report"
- [ ] Report displays:
  - [ ] File information
  - [ ] Authenticity assessment
  - [ ] Component analysis
  - [ ] Forensic findings
  - [ ] Recommendations

### Test 5: View History
- [ ] Navigate to History page
- [ ] Uploaded files visible in table
- [ ] Can filter by verdict
- [ ] Can search by filename
- [ ] Can view file details

### Test 6: Hash Verification
- [ ] Navigate to Integrity Checker
- [ ] Test "Check by File ID" tab:
  - [ ] Enter file ID
  - [ ] Enter correct hash
  - [ ] Verification succeeds
- [ ] Test "Upload New File" tab:
  - [ ] Upload file
  - [ ] Hash calculated and displayed

---

## 🔍 Troubleshooting Checklist

### Backend Won't Start
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] `.env` file exists and configured
- [ ] PostgreSQL is running
- [ ] Port 8000 is not in use
- [ ] Database credentials correct

### Dashboard Won't Start
- [ ] Virtual environment activated
- [ ] Streamlit installed
- [ ] Port 8501 not in use
- [ ] Backend is running first

### Database Connection Errors
- [ ] PostgreSQL service running
- [ ] Credentials in `.env` match database
- [ ] Database `forensic_db` exists
- [ ] User `forensic_user` has privileges
- [ ] Firewall not blocking connection

### Import Errors
- [ ] Correct directory (project root)
- [ ] Virtual environment activated
- [ ] Requirements installed: `pip install -r requirements.txt`
- [ ] Python version 3.9+

---

## ✅ Final Verification

### All Systems Green
- [ ] Backend running (http://localhost:8000)
- [ ] Dashboard running (http://localhost:8501)
- [ ] Database connected
- [ ] Test file uploaded successfully
- [ ] Analysis completed
- [ ] Report generated
- [ ] No errors in logs

### Logs Check
```bash
# View application logs
cat logs/forensic_system.log

# Should see:
# - Successful database connections
# - File processing logs
# - No ERROR level messages (only INFO, WARNING acceptable)
```

---

## 📝 Optional: Airflow Setup Checklist

### Airflow Configuration
- [ ] Set AIRFLOW_HOME: `export AIRFLOW_HOME=./airflow`
- [ ] Initialized: `airflow db init`
- [ ] Created admin user
- [ ] Started webserver: `airflow webserver --port 8080`
- [ ] Started scheduler: `airflow scheduler`
- [ ] Can access: http://localhost:8080
- [ ] Forensic DAG visible in UI

---

## 📊 Performance Verification

### Expected Performance
- [ ] File upload: < 1 second
- [ ] Image analysis: 2-5 seconds
- [ ] Dashboard load: < 2 seconds
- [ ] API response: < 500ms (health check)

### Resource Usage (Normal)
- [ ] Backend memory: ~100-200MB
- [ ] Dashboard memory: ~50-100MB
- [ ] CPU usage: Low (< 20% idle)
- [ ] Database connections: Stable

---

## 🎯 Production Readiness Checklist

### Security
- [ ] Changed default SECRET_KEY
- [ ] Database passwords are strong
- [ ] `.env` is in `.gitignore`
- [ ] No hardcoded credentials
- [ ] File upload size limits configured

### Backup & Recovery
- [ ] Database backup strategy defined
- [ ] Important files backed up
- [ ] Recovery procedure documented

### Monitoring
- [ ] Logs being written to `./logs/`
- [ ] Health endpoint accessible
- [ ] System metrics tracked

---

## ✅ Sign-Off

**Installation Completed By:** ___________________

**Date:** ___________________

**All Checks Passed:** [ ] Yes  [ ] No

**Notes:**
```
________________________________________________
________________________________________________
________________________________________________
```

---

**🎉 If all checks pass, your system is ready for use!**

**Next Steps:**
1. Review [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed usage
2. Run example script: `python scripts/api_example.py`
3. Start analyzing files!

**Support:**
- Check logs: `./logs/forensic_system.log`
- API docs: http://localhost:8000/api/docs
- Open GitHub issue if problems persist
