"""
Integrity Checker Page
Verify file integrity using hash comparison
"""

import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000/api/v1"


def show():
    """Display integrity checker page"""

    st.markdown(
        """
        <div class="page-hero">
            <h2>✅ File Integrity Checker</h2>
            <p>Validate digital integrity with SHA-256 comparison against known trusted hashes.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Two methods: File ID or upload
    tab1, tab2 = st.tabs(["📋 Check by File ID", "⬆️ Upload New File"])
    
    with tab1:
        check_by_file_id()
    
    with tab2:
        check_by_upload()


def check_by_file_id():
    """Check integrity using existing file ID"""
    
    st.markdown("### Verify Existing File")
    st.caption("Use a previously analyzed file ID and expected SHA-256 hash.")
    
    file_id = st.text_input(
        "File ID",
        placeholder="Enter the file ID",
        key="file_id_input"
    )
    
    expected_hash = st.text_input(
        "Expected SHA-256 Hash",
        placeholder="Enter the expected hash value",
        max_chars=64,
        key="expected_hash_input"
    )
    
    if st.button("✅ Verify Integrity", key="verify_btn"):
        if file_id and expected_hash:
            verify_file_integrity(file_id, expected_hash)
        else:
            st.warning("Please provide both File ID and Expected Hash")


def check_by_upload():
    """Check integrity by uploading a file"""
    
    st.markdown("### Upload File for Verification")
    st.caption("Upload a file to compute hash and optionally compare against expected SHA-256.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['jpg', 'jpeg', 'png', 'pdf', 'docx', 'doc'],
        key="upload_verify"
    )
    
    expected_hash = st.text_input(
        "Expected SHA-256 Hash (Optional)",
        placeholder="Leave empty to just calculate hash",
        max_chars=64,
        key="upload_expected_hash"
    )
    
    if uploaded_file and st.button("🔍 Calculate/Verify Hash", key="upload_verify_btn"):
        verify_uploaded_file(uploaded_file, expected_hash if expected_hash else None)


def verify_file_integrity(file_id, expected_hash):
    """Verify integrity of a file by ID"""
    
    with st.spinner("Verifying file integrity..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/verify/hash",
                json={
                    "file_id": file_id,
                    "expected_hash": expected_hash
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                match = result.get('match')
                
                # Display result with appropriate styling
                if match:
                    st.success("✅ FILE INTEGRITY VERIFIED")
                    st.balloons()
                    
                    st.markdown("### Verification Results")
                    st.write(f"**File Name:** {result.get('file_name')}")
                    st.write(f"**Verdict:** {result.get('verdict')}")
                    st.write(f"**Status:** File is intact and has not been modified")
                else:
                    st.error("❌ FILE INTEGRITY COMPROMISED")
                    
                    st.markdown("### Verification Results")
                    st.write(f"**File Name:** {result.get('file_name')}")
                    st.write(f"**Verdict:** {result.get('verdict')}")
                    st.write(f"**Status:** File has been modified since original upload")
                
                # Hash comparison
                st.markdown("### Hash Comparison")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text("Expected Hash:")
                    st.code(result.get('expected_hash'))
                
                with col2:
                    st.text("Actual Hash:")
                    st.code(result.get('actual_hash'))
                
                if not match:
                    st.warning("⚠️ The hashes do not match. This file may have been tampered with.")
                
            elif response.status_code == 404:
                st.error("File not found. Please check the File ID.")
            else:
                st.error(f"Verification failed: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


def verify_uploaded_file(uploaded_file, expected_hash):
    """Verify an uploaded file"""
    
    with st.spinner("Processing file..."):
        try:
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
            }
            
            params = {}
            if expected_hash:
                params["expected_hash"] = expected_hash
            
            response = requests.post(
                f"{API_BASE_URL}/verify/upload",
                files=files,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ File processed successfully")
                
                # Display hash
                st.markdown("### Calculated Hash")
                st.code(result.get('sha256_hash'))
                
                # If verification was requested
                verification = result.get('verification')
                if verification:
                    match = verification.get('match')
                    
                    if match:
                        st.success("✅ Hash matches expected value!")
                        st.balloons()
                    else:
                        st.error("❌ Hash does NOT match expected value!")
                    
                    st.markdown("### Verification")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text("Expected:")
                        st.code(verification.get('expected_hash'))
                    
                    with col2:
                        st.text("Actual:")
                        st.code(result.get('sha256_hash'))
                else:
                    st.info("💡 To verify this hash, enter an expected hash value above.")
                    
                # Copy to clipboard helper
                st.code(result.get('sha256_hash'), language="text")
                st.caption("Copy this hash to verify the file later")
                
            else:
                st.error("File processing failed")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    show()
