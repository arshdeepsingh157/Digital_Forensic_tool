# 🚨 Quick Start Without Full Installation

## If you're experiencing package installation issues, follow these steps:

### Step 1: Install Only Essential Packages

```powershell
.\quick_install.ps1
```

This installs core packages without problematic dependencies.

### Step 2: Skip PostgreSQL for Now

The application can run without PostgreSQL initially. Update your `.env`:

```env
# Comment out PostgreSQL settings
# POSTGRES_USER=forensic_user
# POSTGRES_PASSWORD=password
```

### Step 3: Modify database.py

Comment out PostgreSQL connection in `models/database.py`:

```python
# engine = create_engine(...)
# SessionLocal = sessionmaker(...)
```

### Step 4: Run in MongoDB-Only Mode

The application can store data in MongoDB only for testing.

### Step 5: Start the Application

```powershell
# Start backend
uvicorn backend.main:app --reload

# In another terminal, start dashboard
streamlit run dashboard/app.py
```

## Common Issues

### Pillow Won't Install
- Use latest version: `pip install Pillow` (no version pin)
- Or install from wheel

### psycopg2-binary Fails
- Requires PostgreSQL to be installed first
- Alternative: Use SQLite temporarily
- Or install PostgreSQL from https://www.postgresql.org/download/

### Slow Internet Connection
- Install packages one at a time
- Use `--no-cache-dir` flag
- Consider using a faster network

### Python 3.13 Compatibility
Some packages don't have pre-built wheels for Python 3.13 yet.

**Solution**: Use Python 3.11:
```powershell
# Create new venv with Python 3.11
py -3.11 -m venv .venv311
.venv311\Scripts\activate
pip install -r requirements-working.txt
```

## Minimal Setup

For bare minimum functionality:

```powershell
pip install fastapi uvicorn streamlit pandas
```

Then manually add features as needed.
