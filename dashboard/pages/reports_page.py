"""
Reports Page
View detailed forensic reports
"""

import streamlit as st
import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"


def show():
    """Display reports page"""

    st.markdown(
        """
        <div class="page-hero">
            <h2>📝 Forensic Reports</h2>
            <p>Generate full case reports for a file ID and review system-wide analytics snapshots.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        file_id = st.text_input(
            "Enter File ID",
            placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000"
        )
    with col2:
        st.write("")
        st.write("")
        generate_clicked = st.button("📄 Generate Report", use_container_width=True)

    if generate_clicked and file_id:
        generate_report(file_id)

    st.markdown("---")
    st.markdown("### 📊 System Statistics")
    if st.button("📈 View Statistics"):
        view_statistics()


def generate_report(file_id):
    """Generate and display forensic report for a file"""
    
    try:
        response = requests.get(f"{API_BASE_URL}/reports/file/{file_id}")
        
        if response.status_code == 200:
            report = response.json()
            
            # Report header
            st.success("✅ Report Generated Successfully")
            
            # Report metadata
            metadata = report.get('report_metadata', {})
            st.markdown(f"**Report ID:** {metadata.get('report_id')}")
            st.markdown(f"**Generated:** {metadata.get('generated_at')}")
            st.markdown(f"**Type:** {metadata.get('report_type')}")
            
            st.markdown("---")
            
            # File information
            st.markdown("### 📄 File Information")
            file_info = report.get('file_information', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**File Name:** {file_info.get('file_name')}")
                st.write(f"**File Size:** {file_info.get('file_size')} bytes")
                st.write(f"**Extension:** {file_info.get('file_extension')}")
            
            with col2:
                st.write(f"**SHA-256:** `{file_info.get('sha256_hash')[:32]}...`")
                st.write(f"**Uploaded:** {file_info.get('uploaded_at')}")
                st.write(f"**Processed:** {file_info.get('processed_at')}")
            
            st.markdown("---")
            
            # Authenticity assessment
            st.markdown("### 🎯 Authenticity Assessment")
            assessment = report.get('authenticity_assessment', {})
            
            verdict = assessment.get('verdict')
            score = assessment.get('overall_score')
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Verdict", verdict)
            with col2:
                st.metric("Score", f"{score:.2f}/100")
            with col3:
                st.metric("Confidence", assessment.get('confidence_level'))
            with col4:
                risk = assessment.get('risk_level')
                st.metric("Risk Level", risk)
            
            # Visual score representation
            st.progress(score / 100)
            
            st.markdown("---")
            
            # Component analysis
            st.markdown("### 🔍 Component Analysis")
            components = report.get('component_analysis', {})
            
            for component_name, component_data in components.items():
                with st.expander(f"{component_name.replace('_', ' ').title()} - Score: {component_data.get('score', 0):.1f}"):
                    for key, value in component_data.items():
                        if key != 'score' and key != 'weight':
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            
            st.markdown("---")
            
            # Findings
            st.markdown("### 🔎 Findings")
            findings = report.get('findings', {})
            
            tampering = findings.get('tampering_indicators', {})
            st.write(f"**Tampered Regions Detected:** {tampering.get('regions_detected', 0)}")
            st.write(f"**Anomalies Detected:** {tampering.get('anomalies_detected', 0)}")
            st.write(f"**Total Issues:** {tampering.get('total_issues', 0)}")
            
            # Recommendations
            recommendations = findings.get('recommendations', [])
            if recommendations:
                st.markdown("#### 💡 Recommendations")
                for idx, rec in enumerate(recommendations, 1):
                    st.write(f"{idx}. {rec}")
            
            st.markdown("---")
            
            # Conclusion
            st.markdown("### 📌 Conclusion")
            conclusion = report.get('conclusion', 'No conclusion available.')
            
            if "ALERT" in conclusion:
                st.error(conclusion)
            elif "suspicious" in conclusion.lower():
                st.warning(conclusion)
            else:
                st.success(conclusion)
            
            # Download report option
            st.markdown("---")
            st.download_button(
                label="📥 Download Report (JSON)",
                data=json.dumps(report, indent=2),
                file_name=f"forensic_report_{file_id}.json",
                mime="application/json"
            )
            
        elif response.status_code == 404:
            st.error("❌ File not found. Please check the File ID.")
        else:
            st.error(f"Failed to generate report: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API.")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def view_statistics():
    """View system statistics"""
    
    try:
        response = requests.get(f"{API_BASE_URL}/reports/statistics/overview")
        
        if response.status_code == 200:
            stats = response.json()
            
            st.markdown("### 📊 Overall Statistics")
            overall = stats.get('overall_statistics', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", overall.get('total_files', 0))
            with col2:
                st.metric("Authentic", overall.get('authentic', 0))
            with col3:
                st.metric("Suspicious", overall.get('suspicious', 0))
            with col4:
                st.metric("Tampered", overall.get('tampered', 0))
            
            # Percentages
            st.markdown("#### Percentage Breakdown")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Authentic %", f"{overall.get('authentic_percentage', 0):.2f}%")
            with col2:
                st.metric("Suspicious %", f"{overall.get('suspicious_percentage', 0):.2f}%")
            with col3:
                st.metric("Tampered %", f"{overall.get('tampered_percentage', 0):.2f}%")
        else:
            st.error("Failed to load statistics")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    show()
