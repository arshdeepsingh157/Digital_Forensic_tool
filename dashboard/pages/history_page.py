"""
History Page
View and search processed files
"""

import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8000/api/v1"


def show():
    """Display history page"""

    st.markdown(
        """
        <div class="page-hero">
            <h2>📜 Analysis History</h2>
            <p>Search, filter, and inspect all previously processed files from the forensic pipeline.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Filter options
    col1, col2, col3, col4 = st.columns([1.2, 1, 1.8, 0.8])
    
    with col1:
        verdict_filter = st.selectbox(
            "Filter by Verdict",
            ["All", "Authentic", "Suspicious", "Tampered"]
        )
    
    with col2:
        limit = st.number_input("Results per page", min_value=10, max_value=100, value=50)
    
    with col3:
        search_query = st.text_input("Search", placeholder="File name or hash...")

    with col4:
        st.write("")
        st.write("")
        search_clicked = st.button("🔍 Search", use_container_width=True)
    
    # Search button
    if search_query and search_clicked:
        search_files(search_query)
    else:
        # Load history
        load_history(verdict_filter if verdict_filter != "All" else None, limit)


def load_history(verdict=None, limit=50):
    """Load file history"""
    
    try:
        params = {"limit": limit}
        if verdict:
            params["verdict"] = verdict
        
        response = requests.get(f"{API_BASE_URL}/history", params=params)
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            if files:
                st.info(f"Showing {len(files)} of {data.get('total', 0)} total files")
                
                # Convert to DataFrame for better display
                df = pd.DataFrame(files)
                
                # Format columns
                if 'processed_at' in df.columns:
                    df['processed_at'] = pd.to_datetime(df['processed_at']).dt.strftime('%Y-%m-%d %H:%M')
                
                # Display table
                st.dataframe(
                    df[['file_name', 'verdict', 'overall_score', 'confidence', 'processed_at']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Detail view
                st.markdown("### 📋 File Details")
                selected_file = st.selectbox(
                    "Select a file to view details",
                    options=[(f['file_name'], f['file_id']) for f in files],
                    format_func=lambda x: x[0]
                )
                
                if selected_file:
                    view_file_details(selected_file[1])
                    
            else:
                st.info("No files found matching the criteria.")
        else:
            st.error("Failed to load history")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API.")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def search_files(query):
    """Search for files"""
    
    try:
        response = requests.get(f"{API_BASE_URL}/history/search", params={"query": query})
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            st.success(f"Found {data.get('results_count', 0)} matching files")
            
            if files:
                for file in files:
                    with st.expander(f"📄 {file['file_name']} - {file['verdict']}"):
                        st.write(f"**File ID:** {file['file_id']}")
                        st.write(f"**Hash:** `{file['sha256_hash'][:32]}...`")
                        st.write(f"**Score:** {file['overall_score']:.2f}")
                        st.write(f"**Processed:** {file['processed_at']}")
                        
                        if st.button(f"View Full Report", key=file['file_id']):
                            view_file_details(file['file_id'])
            else:
                st.info("No files found matching your search.")
        else:
            st.error("Search failed")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")


def view_file_details(file_id):
    """View detailed information for a file"""
    
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/{file_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            st.markdown("#### Detailed Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall Score", f"{data.get('overall_score', 0):.2f}")
            with col2:
                st.metric("Verdict", data.get('verdict'))
            with col3:
                st.metric("Confidence", data.get('confidence'))
            
            # Component scores
            scores = data.get('scores', {})
            st.markdown("**Component Scores:**")
            for component, score in scores.items():
                st.write(f"- {component.capitalize()}: {score:.2f}")
            
            # Recommendations
            recommendations = data.get('recommendations', [])
            if recommendations:
                st.markdown("**Recommendations:**")
                for rec in recommendations:
                    st.write(f"- {rec}")
                    
        else:
            st.error("Failed to load file details")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    show()
