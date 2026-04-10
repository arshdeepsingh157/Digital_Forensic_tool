"""
Dashboard Page
Main overview with KPIs and visualizations
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import pandas as pd

API_BASE_URL = "http://localhost:8000/api/v1"


def show():
    """Display dashboard page"""
    
    st.title("📊 Forensic Analytics Dashboard")
    st.markdown("Real-time insights into file authenticity analysis")
    
    # Fetch dashboard data
    try:
        response = requests.get(f"{API_BASE_URL}/reports/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            
            # KPI Section
            st.markdown("### 📈 Key Performance Indicators")
            kpi = data.get('kpi', {})
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Files", kpi.get('total_files', 0))
            
            with col2:
                st.metric(
                    "✅ Authentic",
                    kpi.get('authentic', 0),
                    f"{kpi.get('authentic_rate', 0):.1f}%"
                )
            
            with col3:
                st.metric("⚠️ Suspicious", kpi.get('suspicious', 0))
            
            with col4:
                st.metric("❌ Tampered", kpi.get('tampered', 0))
            
            with col5:
                authentic_rate = kpi.get('authentic_rate', 0)
                st.metric(
                    "Authenticity Rate",
                    f"{authentic_rate:.1f}%",
                    delta=f"{authentic_rate - 50:.1f}%" if authentic_rate > 50 else None
                )
            
            st.markdown("---")
            
            # Charts section
            charts = data.get('charts', {})
            
            # Row 1: Verdict Distribution and Score Distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎯 Verdict Distribution")
                verdict_data = charts.get('verdict_distribution', {})
                
                if verdict_data:
                    fig = go.Figure(data=[go.Pie(
                        labels=list(verdict_data.keys()),
                        values=list(verdict_data.values()),
                        hole=0.4,
                        marker=dict(colors=["#1aa38f", '#f59e0b', '#e5484d'])
                    )])
                    fig.update_layout(
                        template="plotly_white",
                        paper_bgcolor='rgba(255,255,255,0)',
                        plot_bgcolor='rgba(255,255,255,0)',
                        height=350,
                        showlegend=True,
                        margin=dict(t=0, b=0, l=0, r=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available yet. Upload files to see statistics.")
            
            with col2:
                st.markdown("### 📊 Score Distribution")
                score_dist = charts.get('score_distribution', [])
                
                if score_dist:
                    df_scores = pd.DataFrame(score_dist)
                    fig = px.bar(
                        df_scores,
                        x='range',
                        y='count',
                        template="plotly_white",
                        color='count',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(255,255,255,0)',
                        plot_bgcolor='rgba(255,255,255,0)',
                        xaxis_title="Score Range",
                        yaxis_title="File Count",
                        height=350,
                        showlegend=False,
                        margin=dict(t=0, b=0, l=0, r=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available yet.")
            
            st.markdown("---")
            
            # Row 2: Temporal Trends
            st.markdown("### 📅 Temporal Trends (Last 30 Days)")
            trends = charts.get('temporal_trends', [])
            
            if trends:
                df_trends = pd.DataFrame(trends)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_trends['date'],
                    y=df_trends['authentic'],
                    mode='lines+markers',
                    name='Authentic',
                    line=dict(color='#00ff9d', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=df_trends['date'],
                    y=df_trends['suspicious'],
                    mode='lines+markers',
                    name='Suspicious',
                    line=dict(color='#ffaa00', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=df_trends['date'],
                    y=df_trends['tampered'],
                    mode='lines+markers',
                    name='Tampered',
                    line=dict(color='#ff4444', width=2)
                ))
                
                fig.update_layout(
                    template="plotly_white",
                    paper_bgcolor='rgba(255,255,255,0)',
                    plot_bgcolor='rgba(255,255,255,0)',
                    xaxis_title="Date",
                    yaxis_title="File Count",
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No temporal data available yet.")
            
            st.markdown("---")
            
            # Row 3: Top Tampered Files and File Types
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🚨 Top Tampered Files")
                top_tampered = data.get('top_tampered', [])
                
                if top_tampered:
                    for idx, item in enumerate(top_tampered[:5], 1):
                        score = item.get('overall_score', 0)
                        verdict = item.get('verdict', 'Unknown')
                        
                        with st.expander(f"{idx}. {item.get('file_name')} - Score: {score:.1f}"):
                            st.write(f"**File ID:** {item.get('file_id')}")
                            st.write(f"**Verdict:** {verdict}")
                            st.write(f"**Score:** {score:.2f}")
                            st.write(f"**Processed:** {item.get('processed_at', 'N/A')}")
                else:
                    st.info("No tampered files detected yet.")
            
            with col2:
                st.markdown("### 📁 File Type Distribution")
                file_types = charts.get('file_types', {})
                
                if file_types:
                    fig = px.pie(
                        names=list(file_types.keys()),
                        values=list(file_types.values()),
                        template="plotly_white",
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(255,255,255,0)',
                        plot_bgcolor='rgba(255,255,255,0)',
                        height=350,
                        showlegend=True,
                        margin=dict(t=0, b=0, l=0, r=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No file type data available.")
            
            st.markdown("---")
            
            # Performance Metrics
            st.markdown("### ⚡ Performance Metrics")
            perf = data.get('performance', {})
            
            if perf:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Operations", perf.get('total_operations', 0))
                
                with col2:
                    st.metric("Avg Duration", f"{perf.get('avg_duration_seconds', 0):.2f}s")
                
                with col3:
                    st.metric("Min Duration", f"{perf.get('min_duration_seconds', 0):.2f}s")
                
                with col4:
                    st.metric("Max Duration", f"{perf.get('max_duration_seconds', 0):.2f}s")
            
            # Last updated
            st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            st.error(f"Failed to load dashboard data: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Please ensure the FastAPI backend is running.")
        st.info("Start the backend with: `uvicorn backend.main:app --reload`")
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")


if __name__ == "__main__":
    show()
