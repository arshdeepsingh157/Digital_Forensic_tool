"""
Example usage script demonstrating the Digital Forensics System API
"""

import requests
import json
from pathlib import Path


# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def upload_file(file_path: str):
    """Upload a file for analysis"""
    print_section("1. UPLOADING FILE FOR ANALYSIS")
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return None
    
    print(f"📁 File: {file_path.name}")
    print(f"📊 Size: {file_path.stat().st_size / 1024:.2f} KB")
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f)}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Upload successful!")
        print(f"   File ID: {result['file_id']}")
        print(f"   Verdict: {result['verdict']}")
        print(f"   Score: {result['overall_score']:.2f}/100")
        print(f"   Confidence: {result['confidence']}")
        return result['file_id']
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def get_analysis(file_id: str):
    """Get detailed analysis results"""
    print_section("2. RETRIEVING DETAILED ANALYSIS")
    
    response = requests.get(f"{API_BASE_URL}/analysis/{file_id}")
    
    if response.status_code == 200:
        analysis = response.json()
        print(f"\n📊 Component Scores:")
        for component, score in analysis['component_scores'].items():
            print(f"   {component.capitalize():12s}: {score:6.2f}/100")
        
        print(f"\n🎯 Overall Assessment:")
        print(f"   Score: {analysis['overall_score']:.2f}")
        print(f"   Verdict: {analysis['verdict']}")
        print(f"   Confidence: {analysis['confidence']}")
        
        if analysis.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"   • {rec}")
        
        return analysis
    else:
        print(f"❌ Failed to retrieve analysis: {response.status_code}")
        return None


def verify_hash(file_id: str, expected_hash: str):
    """Verify file integrity using hash"""
    print_section("3. VERIFYING FILE INTEGRITY")
    
    payload = {
        "file_id": file_id,
        "expected_hash": expected_hash
    }
    
    response = requests.post(f"{API_BASE_URL}/verify/hash", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result['match']:
            print(f"✅ Hash verification PASSED")
            print(f"   Hash: {result['actual_hash']}")
        else:
            print(f"❌ Hash verification FAILED")
            print(f"   Expected: {expected_hash}")
            print(f"   Actual:   {result['actual_hash']}")
        return result
    else:
        print(f"❌ Verification failed: {response.status_code}")
        return None


def generate_report(file_id: str):
    """Generate forensic report"""
    print_section("4. GENERATING FORENSIC REPORT")
    
    response = requests.get(f"{API_BASE_URL}/reports/{file_id}")
    
    if response.status_code == 200:
        report = response.json()
        print(f"\n📝 Report Generated:")
        print(f"   File: {report.get('file_name', 'N/A')}")
        print(f"   Generated: {report.get('generated_at', 'N/A')}")
        print(f"   Verdict: {report.get('verdict', 'N/A')}")
        
        # Save report to file
        report_file = f"forensic_report_{file_id[:8]}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {report_file}")
        
        return report
    else:
        print(f"❌ Failed to generate report: {response.status_code}")
        return None


def view_history(limit: int = 10, verdict: str = None):
    """View file processing history"""
    print_section("5. VIEWING PROCESSING HISTORY")
    
    params = {"limit": limit}
    if verdict:
        params["verdict"] = verdict
    
    response = requests.get(f"{API_BASE_URL}/history", params=params)
    
    if response.status_code == 200:
        history = response.json()
        print(f"\n📜 Recent Files (showing {len(history['files'])} of {history['total']}):")
        
        for idx, file in enumerate(history['files'], 1):
            print(f"\n   {idx}. {file['file_name']}")
            print(f"      ID: {file['file_id']}")
            print(f"      Verdict: {file['verdict']}")
            print(f"      Score: {file['overall_score']:.2f}")
            print(f"      Processed: {file['processed_at']}")
        
        return history
    else:
        print(f"❌ Failed to retrieve history: {response.status_code}")
        return None


def get_statistics():
    """Get system statistics"""
    print_section("6. SYSTEM STATISTICS")
    
    response = requests.get(f"{API_BASE_URL}/reports/statistics/overview")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"\n📊 System Overview:")
        print(f"   Total Files: {stats.get('total_files', 0)}")
        print(f"   Authentic: {stats.get('authentic_count', 0)}")
        print(f"   Suspicious: {stats.get('suspicious_count', 0)}")
        print(f"   Tampered: {stats.get('tampered_count', 0)}")
        print(f"\n   Average Score: {stats.get('average_score', 0):.2f}")
        print(f"   Authenticity Rate: {stats.get('authenticity_rate', 0):.2f}%")
        
        return stats
    else:
        print(f"❌ Failed to retrieve statistics: {response.status_code}")
        return None


def main():
    """Main demonstration function"""
    print("\n" + "="*70)
    print("  🔍 AI-Powered Digital Forensics System - API Example")
    print("="*70)
    
    # Get file path from user
    file_path = input("\n📁 Enter path to file for analysis: ").strip()
    
    if not file_path:
        print("❌ No file provided. Exiting...")
        return
    
    # Execute workflow
    try:
        # Step 1: Upload and analyze
        file_id = upload_file(file_path)
        
        if not file_id:
            print("\n❌ Upload failed. Cannot continue.")
            return
        
        # Step 2: Get detailed analysis
        analysis = get_analysis(file_id)
        
        # Step 3: Verify hash (using calculated hash)
        if analysis and 'file_hash' in analysis:
            verify_hash(file_id, analysis['file_hash'])
        
        # Step 4: Generate report
        generate_report(file_id)
        
        # Step 5: View recent history
        view_history(limit=5)
        
        # Step 6: Get statistics
        get_statistics()
        
        print_section("✅ DEMONSTRATION COMPLETE")
        print(f"\n💡 Next steps:")
        print(f"   • View dashboard: http://localhost:8501")
        print(f"   • API docs: http://localhost:8000/api/docs")
        print(f"   • Your file ID: {file_id}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("   Make sure the backend is running:")
        print("   > uvicorn backend.main:app --reload")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
