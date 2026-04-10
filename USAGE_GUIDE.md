# 📖 Usage Guide

Complete guide to using the AI-Powered Digital Forensics System.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Usage](#dashboard-usage)
3. [API Usage](#api-usage)
4. [Understanding Results](#understanding-results)
5. [Best Practices](#best-practices)
6. [Advanced Features](#advanced-features)

---

## Getting Started

### Starting the System

1. **Option 1: Quick Start (Windows)**
   ```powershell
   .\start.ps1
   ```

2. **Option 2: Manual Start**
   
   Terminal 1 - Backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
   
   Terminal 2 - Dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```

### Accessing the System

- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/api/docs
- **API Endpoints**: http://localhost:8000/api/v1/

---

## Dashboard Usage

### 📊 Dashboard Page

The main dashboard provides real-time analytics:

**Key Metrics:**
- Total files processed
- Authentic vs Suspicious vs Tampered counts
- Overall authenticity rate

**Visualizations:**
- Verdict distribution (pie chart)
- Score distribution (bar chart)
- Temporal trends (line graph)
- File type breakdown

**Usage:**
1. Navigate to "Dashboard" from sidebar
2. View real-time statistics
3. Monitor processing trends
4. Identify potential issues

### ⬆️ Upload & Analyze Page

Upload files for forensic analysis:

**Single File Upload:**
1. Click "Choose a file to analyze"
2. Select supported file (JPG, PNG, PDF, etc.)
3. Click "Analyze File"
4. Wait for processing (shows progress)
5. View detailed results

**Batch Upload:**
1. Go to "Batch Upload" section
2. Select multiple files
3. Click "Analyze Batch"
4. View summary statistics

**Supported File Types:**
- Images: JPG, JPEG, PNG, BMP, TIFF
- Documents: PDF, DOCX, DOC

**File Size Limit:** 50MB per file

### 📝 Reports Page

Generate detailed forensic reports:

**Steps:**
1. Enter File ID (obtained after analysis)
2. Click "Generate Report"
3. View comprehensive analysis
4. Download as JSON

**Report Includes:**
- File information
- Authenticity assessment
- Component analysis breakdown
- Forensic findings
- Recommendations
- Technical details

**System Statistics:**
- Click "View Statistics" for system-wide metrics
- See overall performance data

### 📜 History Page

Browse and search processed files:

**Features:**
- **Filtering:** Filter by verdict (Authentic/Suspicious/Tampered)
- **Search:** Search by file name or hash
- **Pagination:** Navigate through large datasets
- **Details:** Click on any file to view full analysis

**Usage:**
1. Select filter criteria
2. Adjust results per page
3. Click on files for detailed view
4. Use search for specific files

### ✅ Integrity Checker

Verify file integrity using hash comparison:

**Method 1: Check by File ID**
1. Select "Check by File ID" tab
2. Enter File ID
3. Enter expected SHA-256 hash
4. Click "Verify Integrity"
5. View match/mismatch result

**Method 2: Upload New File**
1. Select "Upload New File" tab
2. Upload file to verify
3. (Optional) Enter expected hash
4. Click "Calculate/Verify Hash"
5. Copy hash for future verification

---

## API Usage

### Authentication

Currently, authentication is optional. To enable:

1. Set `ENABLE_AUTH=True` in `.env`
2. Implement JWT token-based authentication

### Common Endpoints

#### 1. Upload File for Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/file.jpg"
```

**Response:**
```json
{
  "success": true,
  "file_id": "123e4567-e89b-12d3-a456-426614174000",
  "overall_score": 87.5,
  "verdict": "Authentic",
  "confidence": "High"
}
```

#### 2. Get Analysis Results

```bash
curl "http://localhost:8000/api/v1/analysis/{file_id}"
```

#### 3.Verify File Integrity

```bash
curl -X POST "http://localhost:8000/api/v1/verify/hash" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your-file-id",
    "expected_hash": "sha256-hash-value"
  }'
```

#### 4. Get File History

```bash
curl "http://localhost:8000/api/v1/history?limit=50&verdict=Tampered"
```

#### 5. Generate Report

```bash
curl "http://localhost:8000/api/v1/reports/{file_id}"
```

### Python SDK Example

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Upload and analyze file
with open("image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{API_BASE}/upload", files=files)
    result = response.json()
    
    print(f"Verdict: {result['verdict']}")
    print(f"Score: {result['overall_score']}")
    file_id = result['file_id']

# Get detailed analysis
analysis = requests.get(f"{API_BASE}/analysis/{file_id}").json()

# Generate report
report = requests.get(f"{API_BASE}/reports/{file_id}").json()
```

---

## Understanding Results

### Authenticity Score (0-100)

The overall score combines multiple forensic analyses:

**Score Breakdown:**
- **Metadata Analysis (30%)**: EXIF data consistency
- **Hash Verification (30%)**: SHA-256 integrity
- **ELA Analysis (20%)**: Compression artifacts
- **Noise Analysis (20%)**: Pixel-level patterns

### Verdict Categories

| Score Range | Verdict | Description |
|-------------|---------|-------------|
| 90-100 | **Authentic** ✅ | High confidence the file is original |
| 60-89 | **Suspicious** ⚠️ | Some anomalies detected, review recommended |
| 0-59 | **Tampered** ❌ | Strong evidence of modification |

### Confidence Levels

- **High**: All analyses agree (low variance)
- **Medium**: Some disagreement between analyses
- **Low**: Significant disagreement (further investigation needed)

### Component Scores

**Metadata Score:**
- Checks EXIF data consistency
- Detects editing software traces
- Verifies timestamp integrity
- Identifies device mismatches

**Hash Score:**
- Binary comparison (100% or 0%)
- Detects any modification
- Most reliable indicator

**ELA Score:**
- Analyzes compression artifacts
- Detects localized edits
- Highlights modified regions
- Image files only

**Noise Score:**
- Examines pixel noise patterns
- Detects statistical anomalies
- Identifies spliced regions
- Image files only

---

## Best Practices

### File Submission

1. **Use Original Files**: Avoid re-compressed or resized images
2. **Document Chain of Custody**: Record file handling
3. **Multiple Formats**: Analyze both original and copies
4. **Verify Hashes**: Record SHA-256 immediately upon receipt

### Result Interpretation

1. **Consider All Factors**: Don't rely on single metric
2. **Review Confidence**: Low confidence = needs review
3. **Check Recommendations**: Follow system suggestions
4. **Manual Verification**: Use results as guidance, not absolute truth

### Security

1. **Protect File IDs**: Treat as sensitive information
2. **Secure Storage**: Store original files securely
3. **Access Control**: Limit who can delete records
4. **Regular Backups**: Backup database regularly

---

## Advanced Features

### Batch Processing

Process multiple files efficiently:

```python
import requests

files_to_process = ["file1.jpg", "file2.jpg", "file3.jpg"]

for file_path in files_to_process:
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_BASE}/upload", files=files)
        result = response.json()
        print(f"{file_path}: {result['verdict']}")
```

### Airflow Integration

Use Apache Airflow for scheduled processing:

```bash
# Trigger DAG with file path
airflow dags trigger forensic_file_analysis \
  --conf '{"file_path": "/path/to/file.jpg"}'
```

### Programmatic Analysis

Use forensic modules directly:

```python
from utils.scorer import analyze_file_authenticity

# Analyze file
results = analyze_file_authenticity("image.jpg")

# Access component scores
print(f"Metadata: {results['component_scores']['metadata']}")
print(f"Hash: {results['component_scores']['hash']}")
print(f"ELA: {results['component_scores']['ela']}")
print(f"Noise: {results['component_scores']['noise']}")
```

### Custom Scoring Weights

Modify weights in `.env`:

```env
WEIGHT_METADATA=0.40  # Increase metadata importance
WEIGHT_HASH=0.30
WEIGHT_ELA=0.15
WEIGHT_NOISE=0.15
```

Weights must sum to 1.0.

---

## Common Scenarios

### Scenario 1: Verify Evidence Photo

1. Upload photo via dashboard
2. Record File ID and hash immediately
3. Review all component scores
4. Generate and save report
5. If authentic, proceed with case
6. If suspicious/tampered, flag for investigation

### Scenario 2: Bulk Document Verification

1. Use batch upload feature
2. Filter results by verdict
3. Export suspicious files list
4. Review each flagged file manually
5. Generate reports for evidence

### Scenario 3: Ongoing Monitoring

1. Set up Airflow for scheduled scans
2. Monitor dashboard daily
3. Review temporal trends
4. Investigate anomalies
5. Adjust thresholds as needed

---

## Troubleshooting

### Analysis Takes Too Long

- **Cause**: Large file size, complex image
- **Solution**: 
  - Check file size (< 50MB recommended)
  - Ensure backend has sufficient resources
  - Monitor system logs

### Inconsistent Results

- **Cause**: Low-quality input, multiple edits
- **Solution**:
  - Check confidence level
  - Review all component scores
  - Perform manual verification
  - Test with known authentic file

### Cannot Upload File

- **Cause**: Unsupported format, size limit
- **Solution**:
  - Check file extension
  - Verify file size < 50MB
  - Ensure backend is running
  - Check storage permissions

---

## Additional Resources

- **API Documentation**: http://localhost:8000/api/docs
- **Technical Reference**: See `docs/FORENSIC_TECHNIQUES.md`
- **Setup Guide**: See `SETUP.md`
- **Sample Scripts**: See `scripts/examples/`

---

**For additional help, consult the logs at `./logs/forensic_system.log`**
