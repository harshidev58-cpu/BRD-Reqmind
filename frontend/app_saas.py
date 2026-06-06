"""
ReqMind AI - Professional SaaS Dashboard
Uizard-style Modern Product Design
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time
import base64

# Page configuration
st.set_page_config(
    page_title="ReqMind AI - Alignment Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'gmail_connected' not in st.session_state:
    st.session_state.gmail_connected = False
if 'slack_connected' not in st.session_state:
    st.session_state.slack_connected = False
if 'meetings_connected' not in st.session_state:
    st.session_state.meetings_connected = False
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Sample datasets for simulation
SAMPLE_GMAIL_DATA = """From: john.pm@company.com
Subject: Q1 Project Deadline - URGENT

Team, we need to deliver this by March 30 for the Q1 release. This is critical and urgent.
The client is expecting a simple MVP approach.

From: client@external.com  
Subject: Re: Project Timeline

Actually, we need delivery by April 10 to accommodate our internal review process.
We also need a comprehensive solution with all features, not just an MVP.

From: sarah.dev@company.com
Subject: Technical Concerns

The scope keeps changing every week. We initially agreed on basic features,
now the client wants advanced analytics and reporting."""

SAMPLE_SLACK_DATA = """#project-alpha
@john.pm: Simple MVP approach - keep it basic, launch by March 30
@sarah.dev: I disagree, we need a comprehensive solution with all features
@mike.lead: The scope keeps changing every week, causing confusion
@client: We need this by April 10, not March 30
@john.pm: Priority is HIGH - this is urgent
@sarah.dev: Actually, this should be LOW priority given other commitments"""

SAMPLE_MEETING_DATA = """Meeting Transcript - Project Kickoff
Date: 2024-02-15

John (PM): We're targeting March 30 for delivery.
Client: That's too soon. We need April 10 at minimum.
Sarah (Dev): The requirements keep changing. First it was simple, now it's complex.
Mike (Lead): We need to freeze the scope or we'll never finish.
Client: We need all features, not just an MVP.
John (PM): Let's keep it simple for now.
"""

# Custom CSS - Uizard-style Modern Design
st.markdown("""
<style>
    /* Global Styles - Uizard Aesthetic */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #0f1729 50%, #1e2139 75%, #0a0e27 100%);
        background-attachment: fixed;
    }
    
    /* Sidebar - Clean Modern */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #0f1729 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.15);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        padding: 0.5rem 0;
    }
    
    /* Logo Section */
    .logo-container {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 16px;
        margin: 1rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    .logo-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .logo-subtitle {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.5rem;
        letter-spacing: 0.5px;
    }
    
    /* Navigation Buttons */
    .stButton > button {
        width: 100%;
        background: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 1.25rem;
        font-weight: 600;
        font-size: 0.95rem;
        text-align: left;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 0.25rem 0;
        box-shadow: none;
    }
    
    .stButton > button:hover {
        background: rgba(99, 102, 241, 0.15);
        color: #6366f1;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
    }
    
    /* Card Styles - Uizard Clean Design */
    .uizard-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .uizard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .uizard-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(99, 102, 241, 0.3);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .uizard-card:hover::before {
        opacity: 1;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 20px;
        padding: 1.75rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover::after {
        opacity: 1;
    }
    
    .metric-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 16px 48px rgba(99, 102, 241, 0.4);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .metric-subtitle {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Status Badges - Modern Pills */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .status-connected {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.5);
    }
    
    .status-disconnected {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        color: white;
        box-shadow: 0 4px 20px rgba(100, 116, 139, 0.3);
    }
    
    /* Risk Level Badges */
    .risk-badge {
        padding: 1.5rem 2.5rem;
        border-radius: 16px;
        font-weight: 800;
        font-size: 1.75rem;
        text-align: center;
        letter-spacing: 1px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        text-transform: uppercase;
    }
    
    .risk-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        animation: pulse-high 2s infinite;
        box-shadow: 0 12px 40px rgba(239, 68, 68, 0.6);
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        box-shadow: 0 12px 40px rgba(245, 158, 11, 0.6);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 12px 40px rgba(16, 185, 129, 0.6);
    }
    
    @keyframes pulse-high {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.85; transform: scale(1.02); }
    }
    
    /* Gauge Display */
    .gauge-container {
        text-align: center;
        padding: 2rem;
        position: relative;
    }
    
    .gauge-score {
        font-size: 5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        text-shadow: 0 0 60px rgba(99, 102, 241, 0.5);
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.6)); }
        50% { filter: drop-shadow(0 0 40px rgba(139, 92, 246, 0.8)); }
    }
    
    .gauge-label {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 1rem;
    }
    
    /* Integration Cards */
    .integration-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .integration-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .integration-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        transform: translateX(8px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.3);
    }
    
    .integration-card:hover::before {
        opacity: 1;
    }
    
    .integration-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.75rem;
    }
    
    .integration-description {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1.25rem;
    }
    
    /* Primary Action Buttons */
    .primary-button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        font-weight: 700;
        padding: 1rem 2.5rem;
        border-radius: 12px;
        border: none;
        font-size: 1rem;
        letter-spacing: 0.5px;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        text-transform: uppercase;
    }
    
    .primary-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.6);
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    }
    
    /* Alert Cards */
    .alert-card {
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 6px solid;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    .alert-high {
        background: rgba(239, 68, 68, 0.15);
        border-color: #ef4444;
        color: #fca5a5;
    }
    
    .alert-medium {
        background: rgba(245, 158, 11, 0.15);
        border-color: #f59e0b;
        color: #fcd34d;
    }
    
    .alert-low {
        background: rgba(16, 185, 129, 0.15);
        border-color: #10b981;
        color: #6ee7b7;
    }
    
    /* Page Headers */
    .page-header {
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.2);
    }
    
    .page-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .page-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Conflict Cards */
    .conflict-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .conflict-card:hover {
        border-color: rgba(239, 68, 68, 0.6);
        background: rgba(30, 41, 59, 0.8);
        transform: translateX(4px);
    }
    
    /* Text Styles */
    h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
        font-weight: 700;
    }
    
    p, span, div, label {
        color: #cbd5e1 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #7c3aed 0%, #a855f7 100%);
    }
    
    /* Top Bar */
    .top-bar {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        padding: 1rem 2rem;
        margin-bottom: 2rem;
        border-radius: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        color: #e2e8f0 !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        color: #e2e8f0;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Divider */
    hr {
        border-color: rgba(99, 102, 241, 0.2);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Helper Functions
def check_api_status():
    """Check if backend API is reachable."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def simulate_oauth_connection(service_name):
    """Simulate OAuth connection flow with loading animation."""
    progress_text = f"🔄 Connecting to {service_name}..."
    progress_bar = st.progress(0, text=progress_text)
    
    for i in range(100):
        time.sleep(0.02)
        progress_bar.progress(i + 1, text=progress_text)
    
    st.success(f"✅ {service_name} connected successfully!")
    time.sleep(1)
    progress_bar.empty()

def call_alignment_api(project_name, email_text, slack_text, meeting_text):
    """Call backend API for alignment analysis."""
    payload = {
        "projectName": project_name,
        "emailText": email_text if email_text else "",
        "slackText": slack_text if slack_text else "",
        "meetingText": meeting_text if meeting_text else ""
    }
    
    response = requests.post(
        f"{API_BASE_URL}/generate_brd_with_alignment",
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def render_sidebar():
    """Render the modern sidebar navigation."""
    with st.sidebar:
        # Logo Section
        st.markdown("""
        <div class="logo-container">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎯</div>
            <div class="logo-title">ReqMind AI</div>
            <div class="logo-subtitle">Alignment Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation Menu
        st.markdown("### 📍 Navigation")
        
        if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if st.button("🔌 Data Sources", key="nav_sources", use_container_width=True):
            st.session_state.page = 'data_sources'
            st.rerun()
        
        if st.button("🎯 Alignment Analysis", key="nav_analysis", use_container_width=True):
            st.session_state.page = 'analysis'
            st.rerun()
        
        if st.button("📄 BRD History", key="nav_history", use_container_width=True):
            st.session_state.page = 'brd_history'
            st.rerun()
        
        if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
            st.session_state.page = 'settings'
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        # System Status
        st.markdown("### 🔌 System Status")
        api_status = check_api_status()
        
        if api_status:
            st.markdown("""
            <div class="status-badge status-connected">
                ✅ API Connected
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge status-disconnected">
                ❌ API Disconnected
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Connection Status
        if st.session_state.gmail_connected or st.session_state.slack_connected or st.session_state.meetings_connected:
            st.markdown("### 📡 Active Connections")
            if st.session_state.gmail_connected:
                st.markdown("🟢 Gmail")
            if st.session_state.slack_connected:
                st.markdown("🟢 Slack")
            if st.session_state.meetings_connected:
                st.markdown("🟢 Meetings")
        
        st.markdown("---")
        st.caption("© 2024 ReqMind AI")
        st.caption("Version 2.0 - Uizard Edition")


def render_dashboard():
    """Render the main dashboard with key metrics."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">📊 Dashboard</div>
        <div class="page-subtitle">Real-time project alignment intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Top Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Get latest analysis if available
    latest_score = 85
    latest_risk = "LOW"
    conflict_count = 0
    timeline_issues = 0
    
    if st.session_state.current_analysis:
        alignment_data = st.session_state.current_analysis['alignment_analysis']
        latest_score = alignment_data['alignment_score']
        latest_risk = alignment_data['risk_level']
        conflict_count = len(alignment_data['conflicts'])
        timeline_issues = len(alignment_data.get('timeline_mismatches', []))
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Alignment Score</div>
            <div class="metric-value">{latest_score:.0f}</div>
            <div class="metric-subtitle">out of 100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        risk_class = f"risk-{latest_risk.lower()}"
        risk_emoji = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Risk Level</div>
            <div class="metric-value" style="font-size: 2rem;">{risk_emoji.get(latest_risk, "⚪")}</div>
            <div class="metric-subtitle">{latest_risk}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Conflicts</div>
            <div class="metric-value">{conflict_count}</div>
            <div class="metric-subtitle">detected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Timeline Issues</div>
            <div class="metric-value">{timeline_issues}</div>
            <div class="metric-subtitle">mismatches</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Early Warning Alert Section
    st.markdown("### 🚨 Early Warning Alert")
    
    if st.session_state.current_analysis:
        alert_msg = st.session_state.current_analysis['alignment_analysis']['alert']
        alert_class = f"alert-{latest_risk.lower()}"
        st.markdown(f"""
        <div class="alert-card {alert_class}">
            <strong>⚠️ {latest_risk} RISK ALERT:</strong><br>
            {alert_msg}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-card alert-low">
            <strong>✅ System Ready:</strong><br>
            No analysis performed yet. Connect data sources to begin monitoring.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Interactive Panels
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤝 Stakeholder Disagreement")
        st.markdown("""
        <div class="uizard-card">
            <p><strong>Status:</strong> Monitoring active</p>
            <p><strong>Last Check:</strong> 5 minutes ago</p>
            <p><strong>Detected Issues:</strong> {}</p>
        </div>
        """.format(conflict_count), unsafe_allow_html=True)
        
        st.markdown("### 📋 Requirement Stability")
        st.markdown("""
        <div class="uizard-card">
            <p><strong>Volatility:</strong> Low</p>
            <p><strong>Changes (7d):</strong> 2</p>
            <p><strong>Trend:</strong> 📉 Decreasing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📅 Timeline Volatility")
        st.markdown("""
        <div class="uizard-card">
            <p><strong>Consistency:</strong> 85%</p>
            <p><strong>Mismatches:</strong> {}</p>
            <p><strong>Average Delay:</strong> 5 days</p>
        </div>
        """.format(timeline_issues), unsafe_allow_html=True)
        
        st.markdown("### 🔄 Decision Reversals")
        st.markdown("""
        <div class="uizard-card">
            <p><strong>This Week:</strong> 1</p>
            <p><strong>Impact:</strong> Medium</p>
            <p><strong>Status:</strong> 🟡 Monitor</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Action Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run New Analysis", use_container_width=True, type="primary"):
            st.session_state.page = 'data_sources'
            st.rerun()


def render_data_sources():
    """Render the data sources page with integration cards."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🔌 Data Sources</div>
        <div class="page-subtitle">Connected Communication Sources</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 2rem;">
        ReqMind intelligently collects communication from connected sources — manual input only for demo.
    </p>
    """, unsafe_allow_html=True)
    
    # Integration Cards Grid
    col1, col2 = st.columns(2)
    
    with col1:
        # Gmail Integration
        st.markdown("""
        <div class="integration-card">
            <div class="integration-title">📧 Gmail Integration</div>
            <div class="integration-description">
                Sync project emails for requirement and timeline analysis
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.gmail_connected:
            st.markdown('<div class="status-badge status-connected">✅ Connected</div>', unsafe_allow_html=True)
            st.caption("📬 Automatically collecting emails...")
            if st.button("Disconnect Gmail", key="disconnect_gmail"):
                st.session_state.gmail_connected = False
                st.rerun()
        else:
            st.markdown('<div class="status-badge status-disconnected">⚪ Disconnected</div>', unsafe_allow_html=True)
            if st.button("🔗 Connect Gmail", key="connect_gmail", use_container_width=True):
                simulate_oauth_connection("Gmail")
                st.session_state.gmail_connected = True
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Meeting Transcripts
        st.markdown("""
        <div class="integration-card">
            <div class="integration-title">🎤 Meeting Transcripts</div>
            <div class="integration-description">
                Upload transcripts or connect Zoom/Google Meet
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.meetings_connected:
            st.markdown('<div class="status-badge status-connected">✅ Connected</div>', unsafe_allow_html=True)
            st.caption("🎥 Monitoring meeting platforms...")
            if st.button("Disconnect Meetings", key="disconnect_meetings"):
                st.session_state.meetings_connected = False
                st.rerun()
        else:
            uploaded_file = st.file_uploader("Upload Transcript (.txt, .pdf)", type=['txt', 'pdf'], key="transcript_upload")
            if uploaded_file:
                st.success("✅ Transcript uploaded successfully!")
                st.session_state.meetings_connected = True
            
            if st.button("🔗 Connect Zoom/Meet (Demo)", key="connect_meetings", use_container_width=True):
                simulate_oauth_connection("Meeting Platform")
                st.session_state.meetings_connected = True
                st.rerun()
    
    with col2:
        # Slack Integration
        st.markdown("""
        <div class="integration-card">
            <div class="integration-title">💬 Slack Integration</div>
            <div class="integration-description">
                Analyze stakeholder discussions across channels
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.slack_connected:
            st.markdown('<div class="status-badge status-connected">✅ Connected</div>', unsafe_allow_html=True)
            st.caption("💬 Monitoring #project channels...")
            if st.button("Disconnect Slack", key="disconnect_slack"):
                st.session_state.slack_connected = False
                st.rerun()
        else:
            st.markdown('<div class="status-badge status-disconnected">⚪ Disconnected</div>', unsafe_allow_html=True)
            if st.button("🔗 Connect Slack", key="connect_slack", use_container_width=True):
                simulate_oauth_connection("Slack")
                st.session_state.slack_connected = True
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Demo Mode
        st.markdown("""
        <div class="integration-card">
            <div class="integration-title">🎯 Demo Mode</div>
            <div class="integration-description">
                Quick analysis with sample dataset
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Load Sample Dataset", key="load_sample", use_container_width=True):
            with st.spinner("Loading sample data..."):
                time.sleep(1.5)
                st.session_state.gmail_connected = True
                st.session_state.slack_connected = True
                st.session_state.meetings_connected = True
                st.session_state.demo_mode = True
                st.success("✅ Sample data loaded from all sources!")
                time.sleep(1)
                st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Manual Demo Input (Optional)
    with st.expander("📝 Manual Demo Input (Optional)", expanded=False):
        st.caption("For testing purposes only - paste sample communication")
        demo_input = st.text_area(
            "Paste sample conversation",
            height=150,
            placeholder="Enter stakeholder communication for demo analysis..."
        )
        if st.button("🔍 Analyze Demo Input", key="analyze_demo"):
            if demo_input:
                with st.spinner("🔄 Analyzing demo input..."):
                    try:
                        result = call_alignment_api("Demo Project", demo_input, "", "")
                        st.session_state.current_analysis = result
                        st.session_state.analysis_history.append({
                            'timestamp': datetime.now(),
                            'project': "Demo Project",
                            'result': result
                        })
                        st.success("✅ Analysis complete!")
                        time.sleep(1)
                        st.session_state.page = 'analysis'
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
            else:
                st.warning("Please enter some text to analyze")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Auto-Analysis Section
    if st.session_state.gmail_connected or st.session_state.slack_connected or st.session_state.meetings_connected:
        st.markdown("### 🤖 Auto-Ingestion Active")
        st.markdown("""
        <div class="alert-card alert-low">
            <strong>✨ Data Collection Active:</strong><br>
            ReqMind is automatically collecting data from your connected sources.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Analyze Alignment Now", key="analyze_now", use_container_width=True, type="primary"):
                # Collect data from connected sources
                email_data = SAMPLE_GMAIL_DATA if st.session_state.gmail_connected else ""
                slack_data = SAMPLE_SLACK_DATA if st.session_state.slack_connected else ""
                meeting_data = SAMPLE_MEETING_DATA if st.session_state.meetings_connected else ""
                
                with st.spinner("🔄 Analyzing alignment across all sources..."):
                    try:
                        result = call_alignment_api(
                            "Auto-Collected Project",
                            email_data,
                            slack_data,
                            meeting_data
                        )
                        st.session_state.current_analysis = result
                        st.session_state.analysis_history.append({
                            'timestamp': datetime.now(),
                            'project': "Auto-Collected Project",
                            'result': result
                        })
                        st.success("✅ Analysis complete!")
                        time.sleep(1)
                        st.session_state.page = 'analysis'
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")


def render_analysis():
    """Render the alignment analysis results page."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🎯 Alignment Analysis</div>
        <div class="page-subtitle">Detailed alignment intelligence report</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.current_analysis:
        st.markdown("""
        <div class="alert-card alert-medium">
            <strong>⚠️ No Analysis Available:</strong><br>
            Please run an analysis from the Data Sources page to view results.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Data Sources", use_container_width=True):
                st.session_state.page = 'data_sources'
                st.rerun()
        return
    
    result = st.session_state.current_analysis
    alignment_data = result['alignment_analysis']
    brd_data = result['brd']
    
    # Alignment Score Gauge
    score = alignment_data['alignment_score']
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="gauge-container">
            <div class="gauge-label">Alignment Score</div>
            <div class="gauge-score">{score:.0f}</div>
            <div class="gauge-label">out of 100</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Risk Badge
    risk_level = alignment_data['risk_level']
    risk_class = f"risk-{risk_level.lower()}"
    risk_emoji = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="risk-badge {risk_class}">
            {risk_emoji.get(risk_level, "⚪")} {risk_level} Risk
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Alert Message
    st.markdown("### 🚨 Alert Status")
    alert_msg = alignment_data['alert']
    alert_class = f"alert-{risk_level.lower()}"
    st.markdown(f"""
    <div class="alert-card {alert_class}">
        <strong>{risk_emoji.get(risk_level, "⚪")} {risk_level} RISK ALERT:</strong><br>
        {alert_msg}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Component Scores
    st.markdown("### 📊 Component Scores")
    component_scores = alignment_data['component_scores']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Stakeholder Agreement</div>
            <div class="metric-value" style="font-size: 2.5rem;">{component_scores['stakeholder_agreement']:.0f}</div>
            <div class="metric-subtitle">%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Timeline Consistency</div>
            <div class="metric-value" style="font-size: 2.5rem;">{component_scores['timeline_consistency']:.0f}</div>
            <div class="metric-subtitle">%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Requirement Stability</div>
            <div class="metric-value" style="font-size: 2.5rem;">{component_scores['requirement_stability']:.0f}</div>
            <div class="metric-subtitle">%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Decision Volatility</div>
            <div class="metric-value" style="font-size: 2.5rem;">{component_scores['decision_volatility']:.0f}</div>
            <div class="metric-subtitle">%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Conflict Details
    st.markdown("### ⚔️ Conflict List")
    conflicts = alignment_data['conflicts']
    
    if conflicts:
        for i, conflict in enumerate(conflicts, 1):
            severity_color = {
                'high': 'rgba(239, 68, 68, 0.3)',
                'medium': 'rgba(245, 158, 11, 0.3)',
                'low': 'rgba(16, 185, 129, 0.3)'
            }
            severity_emoji = {'high': '🔴', 'medium': '🟠', 'low': '🟢'}
            
            with st.expander(f"Conflict {i}: {conflict['type'].replace('_', ' ').title()}", expanded=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Type:** {conflict['type'].replace('_', ' ').title()}")
                    st.markdown(f"**Description:** {conflict['description']}")
                    st.markdown(f"**Sources:** {', '.join(conflict['sources'])}")
                    st.markdown(f"**💡 Recommendation:** {conflict['recommendation']}")
                
                with col2:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: {severity_color.get(conflict['severity'], 'rgba(100, 116, 139, 0.3)')}; border-radius: 12px;">
                        <div style="font-size: 2rem;">{severity_emoji.get(conflict['severity'], '⚪')}</div>
                        <div style="font-weight: 700; text-transform: uppercase; margin-top: 0.5rem;">{conflict['severity']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-card alert-low">
            <strong>✅ No Conflicts Detected:</strong><br>
            All stakeholders are aligned on project requirements and timelines.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Timeline Mismatches
    if alignment_data.get('timeline_mismatches'):
        st.markdown("### 📅 Timeline Mismatch Breakdown")
        for mismatch in alignment_data['timeline_mismatches']:
            st.markdown(f"""
            <div class="alert-card alert-medium">
                <strong>⏰ Timeline Issue:</strong><br>
                {mismatch['description']}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Requirement Volatility
    if alignment_data.get('requirement_volatility'):
        st.markdown("### 📋 Requirement Volatility Trends")
        volatility = alignment_data['requirement_volatility']
        st.markdown(f"""
        <div class="uizard-card">
            <p><strong>Total Changes:</strong> {volatility.get('total_changes', 0)}</p>
            <p><strong>Trend:</strong> {volatility.get('trend', 'Stable')}</p>
            <p><strong>Impact:</strong> {volatility.get('impact', 'Low')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Decision Reversals
    if alignment_data.get('decision_reversals'):
        st.markdown("### 🔄 Decision Reversals List")
        for reversal in alignment_data['decision_reversals']:
            st.markdown(f"""
            <div class="conflict-card">
                <strong>Decision:</strong> {reversal.get('decision', 'N/A')}<br>
                <strong>Impact:</strong> {reversal.get('impact', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # BRD Section
    st.markdown("### 📄 Generated Business Requirements Document")
    with st.expander("📖 View Complete BRD", expanded=False):
        st.markdown(f"**Project Name:** {brd_data['projectName']}")
        st.markdown(f"**Executive Summary:** {brd_data['executiveSummary']}")
        
        st.markdown("**Business Objectives:**")
        for obj in brd_data['businessObjectives']:
            st.markdown(f"- {obj}")
        
        st.markdown("**Requirements:**")
        for req in brd_data['requirements']:
            priority_emoji = {'High': '🔴', 'Medium': '🟠', 'Low': '🟢'}.get(req['priority'], '⚪')
            st.markdown(f"{priority_emoji} **{req['id']}**: {req['description']} (Priority: {req['priority']})")
        
        st.markdown("**Stakeholders:**")
        for stakeholder in brd_data['stakeholders']:
            st.markdown(f"- **{stakeholder['name']}** - {stakeholder['role']}")
        
        if 'timeline' in brd_data:
            st.markdown(f"**Timeline:** {brd_data['timeline']}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        json_str = json.dumps(result, indent=2)
        st.download_button(
            label="📥 Download Complete Analysis (JSON)",
            data=json_str,
            file_name=f"reqmind_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )


def render_brd_history():
    """Render the BRD history page with analysis archive."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">📄 BRD History</div>
        <div class="page-subtitle">Analysis archive and historical data</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.analysis_history:
        st.markdown("""
        <div class="alert-card alert-medium">
            <strong>📭 No History Available:</strong><br>
            Run your first analysis to see results here.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Data Sources", use_container_width=True):
                st.session_state.page = 'data_sources'
                st.rerun()
        return
    
    st.markdown(f"### 📊 Total Analyses: {len(st.session_state.analysis_history)}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display history in reverse chronological order
    for i, entry in enumerate(reversed(st.session_state.analysis_history)):
        alignment_score = entry['result']['alignment_analysis']['alignment_score']
        risk_level = entry['result']['alignment_analysis']['risk_level']
        conflicts = len(entry['result']['alignment_analysis']['conflicts'])
        timestamp = entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        risk_color = {'HIGH': '#ef4444', 'MEDIUM': '#f59e0b', 'LOW': '#10b981'}
        risk_emoji = {'HIGH': '🔴', 'MEDIUM': '🟠', 'LOW': '🟢'}
        
        with st.expander(f"📋 {entry['project']} - {timestamp}", expanded=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;">Score</div>
                    <div style="font-size: 2rem; font-weight: 800; color: {risk_color[risk_level]};">{alignment_score:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;">Risk</div>
                    <div style="font-size: 1.5rem;">{risk_emoji[risk_level]} {risk_level}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;">Conflicts</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #6366f1;">{conflicts}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;">Date</div>
                    <div style="font-size: 0.9rem; color: #cbd5e1;">{entry['timestamp'].strftime('%m/%d/%Y')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                if st.button("👁️ View Details", key=f"view_{i}", use_container_width=True):
                    st.session_state.current_analysis = entry['result']
                    st.session_state.page = 'analysis'
                    st.rerun()
            
            # Download button for this entry
            json_str = json.dumps(entry['result'], indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"reqmind_{entry['project'].replace(' ', '_')}_{entry['timestamp'].strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key=f"download_{i}"
            )


def render_settings():
    """Render the settings page with configuration options."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">⚙️ Settings</div>
        <div class="page-subtitle">System configuration and preferences</div>
    </div>
    """, unsafe_allow_html=True)
    
    # API Configuration
    st.markdown("### 🔌 API Configuration")
    st.markdown("""
    <div class="uizard-card">
        <p><strong>Backend URL:</strong> {}</p>
        <p><strong>Status:</strong> {}</p>
    </div>
    """.format(API_BASE_URL, "✅ Connected" if check_api_status() else "❌ Disconnected"), unsafe_allow_html=True)
    
    if st.button("🔄 Test API Connection"):
        with st.spinner("Testing connection..."):
            time.sleep(1)
            if check_api_status():
                st.success("✅ API connection successful!")
            else:
                st.error("❌ API connection failed. Please check if the backend is running.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Integration Toggles
    st.markdown("### 🔌 Integration Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Gmail**")
        if st.session_state.gmail_connected:
            st.success("✅ Connected")
            if st.button("Disconnect", key="settings_gmail"):
                st.session_state.gmail_connected = False
                st.rerun()
        else:
            st.info("⚪ Disconnected")
    
    with col2:
        st.markdown("**Slack**")
        if st.session_state.slack_connected:
            st.success("✅ Connected")
            if st.button("Disconnect", key="settings_slack"):
                st.session_state.slack_connected = False
                st.rerun()
        else:
            st.info("⚪ Disconnected")
    
    with col3:
        st.markdown("**Meetings**")
        if st.session_state.meetings_connected:
            st.success("✅ Connected")
            if st.button("Disconnect", key="settings_meetings"):
                st.session_state.meetings_connected = False
                st.rerun()
        else:
            st.info("⚪ Disconnected")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Demo Mode
    st.markdown("### 🎯 Demo Mode")
    demo_enabled = st.checkbox("Enable Demo Mode", value=st.session_state.demo_mode)
    if demo_enabled != st.session_state.demo_mode:
        st.session_state.demo_mode = demo_enabled
        st.rerun()
    
    st.caption("Demo mode uses sample datasets for quick testing")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Scoring Weight Adjusters
    st.markdown("### ⚖️ Scoring Weights")
    st.caption("Adjust the impact of each factor on the alignment score")
    
    conflict_weight = st.slider("Conflict Weight", 1, 20, 10, help="Impact of conflicts on alignment score")
    timeline_weight = st.slider("Timeline Mismatch Weight", 1, 20, 15, help="Impact of timeline mismatches")
    requirement_weight = st.slider("Requirement Change Weight", 1, 20, 5, help="Impact of requirement changes")
    decision_weight = st.slider("Decision Reversal Weight", 1, 20, 8, help="Impact of decision reversals")
    
    st.info(f"Current formula: 100 - (conflicts × {conflict_weight}) - (timeline × {timeline_weight}) - (requirements × {requirement_weight}) - (decisions × {decision_weight})")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Notification Settings
    st.markdown("### 🔔 Notification Settings")
    
    email_alerts = st.checkbox("Email alerts for HIGH risk", value=True)
    slack_notifications = st.checkbox("Slack notifications", value=False)
    desktop_notifications = st.checkbox("Desktop notifications", value=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analysis Settings
    st.markdown("### 🎯 Analysis Settings")
    
    sensitivity = st.slider("Conflict Sensitivity", 1, 10, 5, help="Higher values detect more subtle conflicts")
    tolerance = st.slider("Timeline Tolerance (days)", 1, 30, 7, help="Acceptable timeline variance")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data Management
    st.markdown("### 🗄️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Analysis History", use_container_width=True):
            st.session_state.analysis_history = []
            st.session_state.current_analysis = None
            st.success("✅ History cleared successfully!")
    
    with col2:
        if st.button("🔄 Reset All Connections", use_container_width=True):
            st.session_state.gmail_connected = False
            st.session_state.slack_connected = False
            st.session_state.meetings_connected = False
            st.success("✅ All connections reset!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # About Section
    st.markdown("### ℹ️ About")
    st.markdown("""
    <div class="uizard-card">
        <p><strong>ReqMind AI</strong> - Alignment Intelligence System</p>
        <p><strong>Version:</strong> 2.0 - Uizard Edition</p>
        <p><strong>Design:</strong> Modern SaaS Dashboard</p>
        <p><strong>Backend:</strong> FastAPI + Groq AI</p>
        <p><strong>Frontend:</strong> Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    render_sidebar()
    
    # Route to appropriate page
    if st.session_state.page == 'dashboard':
        render_dashboard()
    elif st.session_state.page == 'data_sources':
        render_data_sources()
    elif st.session_state.page == 'analysis':
        render_analysis()
    elif st.session_state.page == 'brd_history':
        render_brd_history()
    elif st.session_state.page == 'settings':
        render_settings()


if __name__ == "__main__":
    main()
