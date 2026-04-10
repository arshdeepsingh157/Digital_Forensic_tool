# 🔍 AI-Powered Digital Forensics System

A production-ready, AI-driven digital forensics platform for detecting file tampering and ensuring digital authenticity using advanced forensic techniques and data engineering pipelines.

## 🌟 Features

- **File Authenticity Verification**: Detect tampering in images, PDFs, and documents
- **SHA-256 Integrity Checking**: Cryptographic hash-based verification
- **AI-Assisted Forensic Analysis**: 
  - Error Level Analysis (ELA)
  - Noise Inconsistency Detection
  - Metadata Analysis
- **Data Engineering Pipeline**: Modular, scalable architecture with Apache Airflow
- **Authenticity Scoring**: Multi-factor scoring system (0-100 scale)
- **Modern Dashboard**: Real-time forensic insights and reporting
- **Forensic Reports**: Detailed PDF reports with visual evidence

## 🏗️ Architecture

```
Data Ingestion → Processing → Analysis → Storage → Visualization
      ↓              ↓           ↓          ↓           ↓
  File Upload → Forensic → Scoring → Database → Dashboard
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance REST API
- **Python 3.9+**: Core language
- **PostgreSQL**: Structured forensic data
- **MongoDB**: Unstructured reports and logs

### Data Engineering
- **Apache Airflow**: Pipeline orchestration
- **Pandas & NumPy**: Data processing
- **PySpark**: Scalable processing (optional)

### AI/Forensic Processing
- **OpenCV**: Image processing and analysis
- **Pillow**: Image manipulation
- **ExifRead**: Metadata extraction
- **Scikit-learn**: Anomaly detection

### Frontend
- **Streamlit**: Interactive dashboard

## 📊 Authenticity Scoring Algorithm

| Component | Weight | Description |
|-----------|--------|-------------|
| Metadata Integrity | 30% | EXIF data consistency |
| Hash Verification | 30% | SHA-256 integrity |
| ELA Analysis | 20% | Compression artifacts |
| Noise Analysis | 20% | Pixel-level anomalies |

### Score Interpretation
- **90-100**: Authentic ✅
- **60-89**: Suspicious ⚠️
- **0-59**: Tampered ❌

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.9+
PostgreSQL 13+
MongoDB 4.4+
Redis (for Airflow)
```

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd AI_Powered_digital_Forensic_system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Initialize databases**
```bash
python scripts/init_db.py
```

6. **Start services**

Terminal 1 - Backend API:
```bash
uvicorn backend.main:app --reload --port 8000
```

Terminal 2 - Airflow (optional):
```bash
airflow standalone
```

Terminal 3 - Dashboard:
```bash
streamlit run dashboard/app.py
```

## 📁 Project Structure

```
AI_Powered_digital_Forensic_system/
├── backend/
│   ├── api/
│   │   ├── routes/        # API endpoints
│   │   └── controllers/   # Business logic
│   ├── services/          # Core services
│   └── main.py           # FastAPI application
├── pipeline/
│   ├── ingestion/        # Data ingestion layer
│   ├── processing/       # Forensic processing
│   ├── analysis/         # Scoring and analytics
│   └── storage/          # Database operations
├── models/               # Database models
├── utils/
│   ├── hashing.py       # SHA-256 utilities
│   ├── ela.py           # Error Level Analysis
│   ├── metadata.py      # EXIF extraction
│   └── noise.py         # Noise detection
├── dashboard/           # Streamlit UI
├── airflow_dags/       # Airflow pipeline definitions
├── config/             # Configuration files
├── scripts/            # Utility scripts
├── tests/              # Unit and integration tests
└── storage/            # File storage
```

## 🔄 Data Pipeline

### 1. Ingestion Layer
- File upload validation
- Format verification
- Unique ID assignment

### 2. Processing Layer
- Metadata extraction
- Hash generation
- ELA computation
- Noise analysis

### 3. Analysis Layer
- Feature aggregation
- Authenticity scoring
- Anomaly flagging

### 4. Storage Layer
- PostgreSQL: Metadata, hashes, scores
- MongoDB: Reports, logs
- Filesystem: Original and processed files

### 5. Visualization Layer
- Dashboard analytics
- Forensic reports
- Historical trends

## 🖥️ Dashboard Features

### Pages
1. **Dashboard**: KPIs, charts, trends
2. **Upload & Analyze**: File processing interface
3. **Reports**: Detailed forensic analysis
4. **History**: Processed files archive
5. **Integrity Checker**: Hash verification

## 🧪 API Endpoints

```
POST   /api/v1/upload              # Upload file for analysis
GET    /api/v1/analysis/{file_id}  # Get analysis results
POST   /api/v1/verify              # Verify file integrity
GET    /api/v1/reports/{file_id}   # Get forensic report
GET    /api/v1/history             # List processed files
DELETE /api/v1/files/{file_id}     # Delete file record
```

## 🔒 Security Features

- SHA-256 cryptographic hashing
- Input validation and sanitization
- File type verification
- Size limits enforcement
- Rate limiting (optional)
- Authentication (JWT-based, optional)

## 📈 Performance

- Async processing with FastAPI
- Database indexing for fast queries
- Caching with Redis (optional)
- Batch processing for multiple files
- Scalable with PySpark

## 🧩 Forensic Techniques

### Error Level Analysis (ELA)
Detects compression inconsistencies by:
1. Recompressing image at known quality
2. Computing pixel-level differences
3. Highlighting modified regions

### Metadata Analysis
Examines EXIF data for:
- Timestamp inconsistencies
- Device information mismatches
- Software modification traces

### Noise Analysis
Identifies tampering through:
- Pixel noise pattern analysis
- Statistical anomaly detection
- Region-based comparison

## 🎨 UI Theme

- Dark cybersecurity aesthetic
- Responsive design
- Real-time processing indicators
- Interactive visualizations

## 📝 Environment Variables

```env
# Database
POSTGRES_USER=forensic_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=forensic_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

MONGO_URI=mongodb://localhost:27017/forensic_logs

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# Storage
STORAGE_PATH=./storage
MAX_FILE_SIZE=52428800  # 50MB

# Airflow
AIRFLOW_HOME=./airflow
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=backend --cov=pipeline tests/

# Run specific test
pytest tests/test_forensic_modules.py
```

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Forensic Techniques](docs/FORENSIC_TECHNIQUES.md)
- [Pipeline Architecture](docs/PIPELINE_ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Senior Full-Stack Python Developer & Data Engineer

## 🙏 Acknowledgments

- OpenCV community
- FastAPI framework
- Apache Airflow project
- Digital forensics research community

---

**Built with ❤️ for Digital Security**
