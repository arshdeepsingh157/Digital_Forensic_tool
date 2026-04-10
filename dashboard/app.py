"""
AI-Powered Digital Forensics Dashboard
Modern Streamlit Dashboard for Forensic Analysis
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="Digital Forensics System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS locked to light theme
st.markdown("""
<style>
    :root {
        --bg: #0d0f12;
        --surface: #14171a;
        --surface-2: #1a1e23;
        --text: #d4d8de;
        --highlight: #4da674;
        --accent: #4a90e2;
        --warning: #d9a036;
        --danger: #d94a4a;
        --line: #2d343b;
        --font-primary: 'Times New Roman', Times, serif;
    }

    .stApp {
        font-family: var(--font-primary);
        color: var(--text);
        background: var(--bg);
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    /* Hide Streamlit sidebar collapse button */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"] {
        display: none;
    }

    .material-symbols-rounded,
    .material-icons,
    .material-icons-round {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
        font-feature-settings: 'liga';
        -webkit-font-feature-settings: 'liga';
        color: var(--highlight);
    }

    [data-testid="stSidebar"] * {
        font-family: var(--font-primary);
    }

    h1, h2, h3, .stTitle {
        font-family: var(--font-primary);
        color: var(--highlight);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    p, label, .stCaption, .stMarkdown {
        color: var(--text);
        font-family: var(--font-primary);
    }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 14px 16px;
        position: relative;
    }
    
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 2px;
        background: var(--highlight);
    }

    [data-testid="stMetricLabel"] {
        color: var(--text);
        font-weight: 700;
        font-size: 0.88rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-family: var(--font-primary);
        font-weight: 700;
    }

    .stButton > button {
        border: none;
        background: transparent;
        color: var(--text);
        font-weight: 600;
        padding: 0.55rem 0.5rem;
        font-family: var(--font-primary);
        text-transform: uppercase;
        box-shadow: none !important;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: transparent;
        color: var(--highlight);
        border: none;
        box-shadow: none;
    }
    
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        border-bottom: 2px solid var(--highlight);
        border-radius: 0;
        color: var(--highlight) !important;
        background: transparent !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 4px;
        background: var(--surface);
    }

    [data-testid="stAlert"] {
        border-radius: 4px;
        border-right: 2px solid;
    }

    [data-testid="stTextInputRootElement"] > div,
    [data-testid="stNumberInputContainer"] > div,
    [data-testid="stSelectbox"] > div,
    [data-testid="stTextArea"] > div {
        border-radius: 2px;
        background: var(--surface);
        border: 1px solid var(--line);
        color: var(--text);
        font-family: var(--font-primary);
    }

    [data-testid="stTextInputRootElement"]:focus-within > div,
    [data-testid="stNumberInputContainer"]:focus-within > div,
    [data-testid="stSelectbox"]:focus-within > div,
    [data-testid="stTextArea"]:focus-within > div {
        border-color: var(--highlight);
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed var(--line);
        border-radius: 4px;
        background: var(--surface);
        color: var(--text);
    }
    
    [data-testid="stFileUploaderDropzone"] button {
        color: var(--highlight) !important;
    }

    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.4rem;
        border-bottom: 1px solid var(--line);
    }

    [data-testid="stTabs"] [role="tab"] {
        border-radius: 4px 4px 0 0;
        border: 1px solid transparent;
        border-bottom: none;
        background: transparent;
        color: var(--text);
        padding: 0.5rem 0.95rem;
        font-family: var(--font-primary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        background: var(--surface);
        color: var(--highlight);
        border: 1px solid var(--line);
        border-bottom: none;
    }

    .page-hero {
        background: var(--surface);
        border: 1px solid var(--line);
        border-left: 3px solid var(--highlight);
        border-radius: 0 4px 4px 0;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    
    .page-hero::before {
        content: 'SYS.INFO';
        position: absolute;
        top: 0; right: 0;
        background: var(--line);
        color: var(--text);
        font-size: 0.6rem;
        padding: 2px 6px;
        font-family: var(--font-primary);
        border-bottom-left-radius: 4px;
    }

    .page-hero h2 {
        margin: 0;
        font-size: 1.55rem;
        color: #fff;
    }

    .page-hero p {
        margin: 0.3rem 0 0 0;
        color: var(--text);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 4px;
        overflow: hidden;
    }

    .block-container {
        padding-top: 2rem;
    }

    .brand-title {
        display: flex;
        align-items: center;
        height: 100%;
        padding-top: 0.15rem;
    }

    .brand-icon {
        font-size: 1.5rem;
        color: var(--highlight);
        margin-right: 0.4rem;
    }

    .brand-text {
        font-family: var(--font-primary);
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #fff;
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

nav_items = [
    "📊 DASHBOARD",
    "⬆️ UPLOAD",
    "📝 REPORTS",
    "📜 HISTORY",
    "✅ INTEGRITY",
]

if "page" not in st.session_state:
    st.session_state.page = nav_items[0]

def navigate_to(page_name):
    st.session_state.page = page_name

# Single top navbar integrating brand and navigation buttons
nav_cols = st.columns([1.8, 1, 1, 1, 1, 1])

with nav_cols[0]:
    st.markdown(
        """
        <div class="brand-title">
            <span class="brand-icon">🔎</span>
            <span class="brand-text">DIGITAL FORENSICS TOOL</span>
        </div>
        """,
        unsafe_allow_html=True
    )

for idx, nav_item in enumerate(nav_items):
    is_active = st.session_state.page == nav_item
    with nav_cols[idx + 1]:
        st.button(
            nav_item,
            key=f"top_nav_{nav_item}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            on_click=navigate_to,
            args=(nav_item,)
        )

page = st.session_state.page

st.markdown("---")

# Import page modules
if page == "📊 DASHBOARD":
    from dashboard.pages import dashboard_page
    dashboard_page.show()
elif page == "⬆️ UPLOAD":
    from dashboard.pages import upload_page
    upload_page.show()
elif page == "📝 REPORTS":
    from dashboard.pages import reports_page
    reports_page.show()
elif page == "📜 HISTORY":
    from dashboard.pages import history_page
    history_page.show()
elif page == "✅ INTEGRITY":
    from dashboard.pages import integrity_page
    integrity_page.show()

# Footer in main page area
st.markdown("---")
st.markdown(
    """
    <div style="
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 14px 18px;
        margin-top: 10px;
        color: var(--text);
        font-family: var(--font-primary);
        text-align: center;
        position: relative;
    ">
        <div style="position: absolute; top: -1px; left: 0; width: 100%; height: 1px; background: var(--line);"></div>
        <div style="font-weight: 700; color: var(--highlight); margin-bottom: 6px; letter-spacing: 0.05em;">
            >_ AI-POWERED DIGITAL FORENSICS SYSTEM
        </div>
        <div style="margin-bottom: 4px; color: var(--accent);">SYS.VERSION: 1.0.0 [SECURE]</div>
        <div style="font-size: 0.85em; opacity: 0.8; margin-top: 8px;">
            [ SHA-256 HASHING ] | [ METADATA ANALYSIS ] | [ ERROR LEVEL ANALYSIS (ELA) ] | [ NOISE PATTERN DETECTION ]
        </div>
        <div style="margin-top: 8px; opacity: 0.6; font-size: 0.7em;">© 2026 DIGITAL FORENSICS COMMAND CENTER. UNAUTHORIZED ACCESS STRICTLY PROHIBITED.</div>
    </div>
    """,
    unsafe_allow_html=True
)
