# 🚀 Setup Guide

Complete step-by-step setup instructions for the AI-Powered Digital Forensics System.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL 13+** ([Download](https://www.postgresql.org/download/))
- **MongoDB 4.4+** ([Download](https://www.mongodb.com/try/download/community)) - Optional but recommended
- **Git** ([Download](https://git-scm.com/downloads))

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd AI_Powered_digital_Forensic_system
```

## Step 2: Create Virtual Environment

### Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI & Uvicorn (Backend)
- Streamlit (Dashboard)
- PostgreSQL & MongoDB drivers
- OpenCV & PIL (Image processing)
- Apache Airflow (Pipeline orchestration)
- And many more...

## Step 4: Database Setup

### PostgreSQL Setup

1. **Install PostgreSQL**
   - Download and install from [postgresql.org](https://www.postgresql.org/download/)

2. **Create Database and User**

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE forensic_db;

-- Create user
CREATE USER forensic_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE forensic_db TO forensic_user;

-- Exit
\q
```

### MongoDB Setup (Optional)

1. **Install MongoDB**
   - Download and install from [mongodb.com](https://www.mongodb.com/try/download/community)

2. **Start MongoDB Service**

**Windows:**
```powershell
net start MongoDB
```

**Linux:**
```bash
sudo systemctl start mongod
```

**Mac:**
```bash
brew services start mongodb-community
```

## Step 5: Environment Configuration

1. **Copy environment template**

```bash
cp .env.example .env
```

2. **Edit .env file** with your configuration:

```env
# PostgreSQL
POSTGRES_USER=forensic_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=forensic_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=forensic_logs

# API
API_PORT=8000
SECRET_KEY=generate_your_secret_key_here

# Storage
STORAGE_PATH=./storage
MAX_FILE_SIZE=52428800
```

3. **Generate Secret Key** (Optional but recommended):

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and use it as your `SECRET_KEY` in `.env`

## Step 6: Initialize Database

Run the database initialization script:

```bash
python scripts/init_db.py
```

This will:
- Create all necessary database tables
- Test database connections
- Create required directories

Expected output:
```
✅ PostgreSQL connection successful
✅ MongoDB connection successful
✅ Database tables created successfully
```

## Step 7: Start the Application

You need to run **two separate processes**:

### Terminal 1: Start Backend API

```bash
uvicorn backend.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
INFO:     Started server process
```

API will be available at:
- **API Endpoints**: http://localhost:8000/api/v1/
- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Terminal 2: Start Dashboard

```bash
streamlit run dashboard/app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

## Step 8: Verify Installation

1. **Open your browser** and navigate to:
   - Dashboard: http://localhost:8501
   - API Docs: http://localhost:8000/api/docs

2. **Test the system**:
   - Go to "Upload & Analyze" in the dashboard
   - Upload a test image
   - Wait for analysis to complete
   - View results

## Optional: Apache Airflow Setup

If you want to use Airflow for pipeline orchestration:

### 1. Initialize Airflow

```bash
export AIRFLOW_HOME=./airflow  # Linux/Mac
# OR
set AIRFLOW_HOME=./airflow     # Windows

airflow db init
```

### 2. Create Admin User

```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 3. Start Airflow

**Terminal 3 (Airflow Webserver):**
```bash
airflow webserver --port 8080
```

**Terminal 4 (Airflow Scheduler):**
```bash
airflow scheduler
```

Access Airflow at: http://localhost:8080

## Troubleshooting

### Issue: Cannot connect to PostgreSQL

**Solution:**
- Ensure PostgreSQL service is running
- Check credentials in `.env` file
- Verify PostgreSQL is listening on localhost:5432

### Issue: Cannot connect to MongoDB

**Solution:**
- Ensure MongoDB service is running
- MongoDB is optional - system will work without it
- Check MongoDB URI in `.env` file

### Issue: Import errors

**Solution:**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port already in use

**Solution:**
```bash
# Change ports in configuration
# Backend: Edit API_PORT in .env
# Dashboard: Use --server.port flag
streamlit run dashboard/app.py --server.port 8502
```

### Issue: File upload fails

**Solution:**
- Check file size (default limit: 50MB)
- Ensure storage directories exist
- Check file permissions

## Development Tips

### Running Tests

```bash
pytest tests/
```

###  Viewing Logs

Logs are stored in `./logs/forensic_system.log`

```bash
# Tail logs in real-time
tail -f logs/forensic_system.log
```

### Database Shell

**PostgreSQL:**
```bash
psql -U forensic_user -d forensic_db
```

**MongoDB:**
```bash
mongo forensic_logs
```

## Production Deployment

For production deployment, additional steps are needed:

1. **Use production-grade database servers**
2. **Configure proper authentication**
3. **Set up HTTPS/SSL**
4. **Use environment-specific configurations**
5. **Set up monitoring and logging**
6. **Configure backup strategies**

See `docs/DEPLOYMENT.md` for detailed production deployment guide.

## Next Steps

Once setup is complete:

1. 📖 Read the [User Guide](docs/USER_GUIDE.md)
2. 🔍 Explore [API Documentation](http://localhost:8000/api/docs)
3. 🧪 Run [Example Scripts](scripts/examples/)
4. 📚 Check out [Forensic Techniques](docs/FORENSIC_TECHNIQUES.md)

## Support

If you encounter any issues:

1. Check the [FAQ](docs/FAQ.md)
2. Review logs in `./logs/`
3. Open an issue on GitHub
4. Contact support

---

**Congratulations! Your Digital Forensics System is now ready to use! 🎉**
