"""
Upload & Analyze Page
Upload files for forensic analysis
"""

import streamlit as st
import requests
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"


def show():
    """Display upload and analyze page"""

    st.markdown(
        """
        <div class="page-hero">
            <h2>⬆️ Upload and Analyze</h2>
            <p>Run single-file or batch forensic analysis with metadata, hash, ELA, and noise checks.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    single_tab, batch_tab = st.tabs(["🔎 Single File", "📦 Batch Analysis"])

    with single_tab:
        uploaded_file = st.file_uploader(
            "Choose a file to analyze",
            type=['jpg', 'jpeg', 'png', 'pdf', 'docx', 'doc'],
            help="Supported formats: JPG, JPEG, PNG, PDF, DOCX, DOC (Max 50MB)",
            key="single_upload"
        )

        if uploaded_file is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Name", uploaded_file.name)
            with col2:
                file_size_mb = uploaded_file.size / (1024 * 1024)
                st.metric("File Size", f"{file_size_mb:.2f} MB")
            with col3:
                st.metric("MIME Type", uploaded_file.type or "N/A")

            if st.button("🔍 Analyze File", type="primary"):
                analyze_file(uploaded_file)

    with batch_tab:
        st.caption("Upload multiple files and process them in one pass.")
        batch_files = st.file_uploader(
            "Choose multiple files",
            type=['jpg', 'jpeg', 'png', 'pdf'],
            accept_multiple_files=True,
            key="batch_upload"
        )

        if batch_files:
            st.info(f"Selected {len(batch_files)} files for batch analysis")

            if st.button("🚀 Analyze Batch", type="primary"):
                analyze_batch(batch_files)


def analyze_file(uploaded_file):
    """Analyze a single file"""
    
    # Progress indicator
    with st.spinner("🔄 Analyzing file... This may take a few moments."):
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Stage 1: Upload
            status_text.text("Stage 1/5: Uploading file...")
            progress_bar.progress(20)
            
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    # Simulate processing stages for UX
                    stages = [
                        ("Stage 2/5: Extracting metadata...", 40),
                        ("Stage 3/5: Calculating hashes...", 60),
                        ("Stage 4/5: Performing ELA analysis...", 80),
                        ("Stage 5/5: Generating report...", 100)
                    ]
                    
                    for stage_text, progress in stages:
                        status_text.text(stage_text)
                        progress_bar.progress(progress)
                        time.sleep(0.3)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results
                    display_analysis_results(result)
                else:
                    st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
            else:
                st.error(f"Upload failed: HTTP {response.status_code}")
                st.error(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Please ensure the FastAPI backend is running.")
            st.info("Start the backend with: `uvicorn backend.main:app --reload`")
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
        finally:
            progress_bar.empty()
            status_text.empty()


def display_analysis_results(result):
    """Display analysis results in a nice format"""
    
    st.success("✅ Analysis Complete!")
    
    # Overall verdict
    verdict = result.get('verdict', 'Unknown')
    overall_score = result.get('overall_score', 0)
    confidence = result.get('confidence', 'Unknown')
    
    st.markdown("### 🎯 Analysis Results")
    
    # Verdict display with color
    verdict_class = "verdict-authentic" if verdict == "Authentic" else (
        "verdict-suspicious" if verdict == "Suspicious" else "verdict-tampered"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<p class="{verdict_class}">{verdict}</p>', unsafe_allow_html=True)
        st.caption("Verdict")
    
    with col2:
        st.metric("Authenticity Score", f"{overall_score:.2f}/100")
    
    with col3:
        st.metric("Confidence", confidence)
    
    st.markdown("---")
    
    # Component scores
    st.markdown("### 📊 Component Scores")
    
    component_scores = result.get('component_scores', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metadata_score = component_scores.get('metadata', 0)
        st.metric("Metadata", f"{metadata_score:.1f}", help="EXIF data consistency")
        st.progress(metadata_score / 100)
    
    with col2:
        hash_score = component_scores.get('hash', 0)
        st.metric("Hash", f"{hash_score:.1f}", help="SHA-256 verification")
        st.progress(hash_score / 100)
    
    with col3:
        ela_score = component_scores.get('ela', 0)
        st.metric("ELA", f"{ela_score:.1f}", help="Error Level Analysis")
        st.progress(ela_score / 100)
    
    with col4:
        noise_score = component_scores.get('noise', 0)
        st.metric("Noise", f"{noise_score:.1f}", help="Noise pattern analysis")
        st.progress(noise_score / 100)
    
    st.markdown("---")
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    
    if recommendations:
        st.markdown("### 💡 Recommendations")
        for idx, rec in enumerate(recommendations, 1):
            if "DO NOT TRUST" in rec or "ALERT" in rec:
                st.error(f"{idx}. {rec}")
            elif "suspicious" in rec.lower() or "warning" in rec.lower():
                st.warning(f"{idx}. {rec}")
            else:
                st.info(f"{idx}. {rec}")
    
    st.markdown("---")
    
    # File details
    with st.expander("📄 File Details"):
        st.write(f"**File ID:** `{result.get('file_id')}`")
        st.write(f"**File Name:** {result.get('file_name')}")
        st.write(f"**Processing Time:** {result.get('processing_time_seconds', 0):.2f} seconds")
        st.write(f"**Timestamp:** {result.get('timestamp')}")


def analyze_batch(batch_files):
    """Analyze multiple files in batch"""
    
    st.markdown("### 📊 Batch Analysis Progress")
    
    progress_bar = st.progress(0)
    results_container = st.container()
    
    total_files = len(batch_files)
    results = []
    
    for idx, file in enumerate(batch_files):
        progress = (idx + 1) / total_files
        progress_bar.progress(progress)
        
        st.write(f"Analyzing {idx + 1}/{total_files}: {file.name}")
        
        try:
            files = {"file": (file.name, file.getvalue(), file.type)}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                results.append(result)
            else:
                st.error(f"Failed to analyze {file.name}")
                
        except Exception as e:
            st.error(f"Error analyzing {file.name}: {str(e)}")
    
    progress_bar.empty()
    
    # Display batch summary
    st.markdown("### 📈 Batch Analysis Summary")
    
    successful = sum(1 for r in results if r.get('success'))
    authentic = sum(1 for r in results if r.get('verdict') == 'Authentic')
    suspicious = sum(1 for r in results if r.get('verdict') == 'Suspicious')
    tampered = sum(1 for r in results if r.get('verdict') == 'Tampered')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", total_files)
    with col2:
        st.metric("✅ Authentic", authentic)
    with col3:
        st.metric("⚠️ Suspicious", suspicious)
    with col4:
        st.metric("❌ Tampered", tampered)
    
    # Detailed results
    with st.expander("📋 Detailed Results"):
        for result in results:
            if result.get('success'):
                st.write(f"**{result.get('file_name')}** - {result.get('verdict')} ({result.get('overall_score'):.1f})")


if __name__ == "__main__":
    show()
