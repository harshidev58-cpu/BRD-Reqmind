"""
ReqMind AI - Modern v0-Styled Dashboard
Enhanced Streamlit frontend with v0-inspired design
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ReqMind AI - Alignment Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with v0-inspired styling
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(to bottom, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Header styles */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Card styles - v0 inspired */
    .v0-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .v0-card:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Input styles */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styles - v0 inspired */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    /* Risk level badges */
    .risk-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .risk-high {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .risk-medium {
        background: #fef3c7;
        color: #92400e;
    }
    
    .risk-low {
        background: #d1fae5;
        color: #065f46;
    }
    
    /* Alert boxes */
    .alert-box {
        background: white;
        border-left: 4px solid #667eea;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .alert-error {
        border-left-color: #ef4444;
        background: #fef2f2;
    }
    
    .alert-warning {
        border-left-color: #f59e0b;
        background: #fffbeb;
    }
    
    .alert-success {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    
    /* Conflict cards */
    .conflict-card {
        background: white;
        border: 1px solid #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: white;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Success/Error messages */
    .element-container .stSuccess,
    .element-container .stError,
    .element-container .stWarning,
    .element-container .stInfo {
        border-radius: 8px;
        border: 1px solid;
    }
    
    /* Label styling */
    label {
        font-weight: 500 !important;
        color: #334155 !important;
        font-size: 0.875rem !important;
    }
    
    /* Helper text */
    .helper-text {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = f"{API_BASE_URL}/generate_brd_with_alignment"
DATASET_ENDPOINT = f"{API_BASE_URL}/dataset/generate_brd_from_dataset"

def check_api_status():
    """Check if the backend API is reachable."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def call_alignment_api(project_name, email_text, slack_text, meeting_text):
    """Call the backend API for alignment analysis."""
    payload = {
        "projectName": project_name,
        "emailText": email_text if email_text else None,
        "slackText": slack_text if slack_text else None,
        "meetingText": meeting_text if meeting_text else None
    }
    
    response = requests.post(API_ENDPOINT, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def call_dataset_api(project_name, keywords, sample_size):
    """Call the dataset-based BRD generation API."""
    payload = {
        "projectName": project_name,
        "keywords": keywords if keywords else None,
        "sampleSize": sample_size
    }
    
    response = requests.post(DATASET_ENDPOINT, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def render_sidebar():
    """Render the sidebar with modern styling."""
    with st.sidebar:
        st.markdown("### 🎯 ReqMind AI")
        st.markdown("**Alignment Intelligence System**")
        st.markdown("---")
        
        # API Status with modern badge
        st.markdown("### 🔌 Connection Status")
        api_status = check_api_status()
        if api_status:
            st.markdown('<div class="alert-box alert-success">✅ Backend Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-error">❌ Backend Disconnected</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Features
        st.markdown("### ✨ Features")
        st.markdown("""
        - 🔍 Conflict Detection
        - 📅 Timeline Analysis
        - 📊 Volatility Tracking
        - 🎯 Alignment Scoring
        - 📄 BRD Generation
        """)
        
        st.markdown("---")
        
        # Risk levels guide
        st.markdown("### 📊 Risk Levels")
        st.markdown('<span class="risk-badge risk-high">HIGH</span> < 70%', unsafe_allow_html=True)
        st.markdown('<span class="risk-badge risk-medium">MEDIUM</span> 70-85%', unsafe_allow_html=True)
        st.markdown('<span class="risk-badge risk-low">LOW</span> > 85%', unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("© 2024 ReqMind AI | v2.0")

def main():
    """Main application function."""
    render_sidebar()
    
    # Main header with gradient
    st.markdown('<h1 class="main-header">🎯 ReqMind AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Project Alignment Intelligence Dashboard</p>', unsafe_allow_html=True)
    
    # Tabs for different modes
    tab1, tab2 = st.tabs(["📝 Manual Input", "🤖 Autonomous Analysis"])
    
    with tab1:
        render_manual_input_tab()
    
    with tab2:
        render_autonomous_tab()

def render_manual_input_tab():
    """Render the manual input tab with v0 styling."""
    st.markdown("## Generate BRD with Alignment Analysis")
    st.markdown('<p class="helper-text">Analyze stakeholder communication from multiple channels</p>', unsafe_allow_html=True)
    
    # Input form in a card
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            project_name = st.text_input(
                "Project Name *",
                placeholder="e.g., Q1 Platform Release",
                help="Enter a descriptive name for your project"
            )
        
        with col2:
            if st.button("📋 Load Sample", use_container_width=True):
                st.session_state['sample_loaded'] = True
                st.rerun()
        
        # Sample data
        if st.session_state.get('sample_loaded', False):
            default_email = "PM: We need delivery by March 30. This is critical for Q1 release."
            default_slack = "I think April 10 is more realistic given the scope."
            default_meeting = "Let's target early April to be safe."
        else:
            default_email = ""
            default_slack = ""
            default_meeting = ""
        
        st.markdown("### 📧 Communication Channels")
        st.markdown('<p class="helper-text">Provide at least one source of communication</p>', unsafe_allow_html=True)
        
        email_text = st.text_area(
            "Email Communications",
            value=default_email,
            height=100,
            placeholder="Paste email content related to the project...",
            help="Email discussions about the project"
        )
        
        slack_text = st.text_area(
            "Slack Messages",
            value=default_slack,
            height=100,
            placeholder="Paste Slack messages related to the project...",
            help="Slack conversations about the project"
        )
        
        meeting_text = st.text_area(
            "Meeting Transcripts",
            value=default_meeting,
            height=100,
            placeholder="Paste meeting transcript content...",
            help="Meeting notes or transcripts"
        )
        
        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button("🚀 Generate BRD & Analysis", use_container_width=True, type="primary")
    
    # Process analysis
    if analyze_button:
        if not project_name.strip():
            st.error("⚠️ Please enter a project name.")
            return
        
        if not email_text.strip() and not slack_text.strip() and not meeting_text.strip():
            st.error("⚠️ Please provide at least one source (email, slack, or meeting).")
            return
        
        with st.spinner("🔄 Analyzing alignment... This may take a few seconds."):
            try:
                result = call_alignment_api(
                    project_name,
                    email_text.strip() or None,
                    slack_text.strip() or None,
                    meeting_text.strip() or None
                )
                
                st.session_state['analysis_result'] = result
                st.session_state['analysis_timestamp'] = datetime.now()
                st.success("✅ Analysis complete!")
                st.rerun()
                
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend API. Please ensure the server is running.")
                return
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                return
    
    # Display results
    if 'analysis_result' in st.session_state:
        render_analysis_results(st.session_state['analysis_result'])

def render_autonomous_tab():
    """Render the autonomous analysis tab."""
    st.markdown("## 🤖 Autonomous Dataset Analysis")
    st.markdown('<p class="helper-text">Analyze data from Enron emails and AMI meeting transcripts</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        project_name = st.text_input(
            "Project Name *",
            value="Autonomous Analysis Project",
            placeholder="Enter project name"
        )
    
    with col2:
        sample_size = st.number_input(
            "Sample Size",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            help="Number of items to sample"
        )
    
    keywords_input = st.text_input(
        "Keywords (comma-separated)",
        value="project, deadline, requirement, feature",
        placeholder="e.g., project, deadline, requirement",
        help="Filter dataset content by these keywords"
    )
    
    keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    
    # Preset buttons
    st.markdown("### 🎬 Quick Presets")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📅 Timeline Conflicts", use_container_width=True):
            st.session_state['preset_keywords'] = "deadline, timeline, delivery, schedule"
            st.rerun()
    
    with col2:
        if st.button("📋 Requirements", use_container_width=True):
            st.session_state['preset_keywords'] = "requirement, feature, specification, scope"
            st.rerun()
    
    with col3:
        if st.button("⚔️ Conflicts", use_container_width=True):
            st.session_state['preset_keywords'] = "disagree, concern, issue, problem"
            st.rerun()
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze from Datasets", use_container_width=True, type="primary"):
            with st.spinner("🤖 Autonomous analysis in progress..."):
                try:
                    result = call_dataset_api(project_name, keywords, sample_size)
                    st.session_state['dataset_result'] = result
                    st.success("✅ Autonomous analysis complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def render_analysis_results(result):
    """Render analysis results with modern styling."""
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    alignment_data = result['alignment_analysis']
    brd_data = result['brd']
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Alignment Score", f"{alignment_data['alignment_score']:.1f}")
    
    with col2:
        risk_level = alignment_data['risk_level']
        risk_class = f"risk-{risk_level.lower()}"
        st.markdown(f'<div class="metric-card"><span class="risk-badge {risk_class}">{risk_level}</span></div>', unsafe_allow_html=True)
    
    with col3:
        st.metric("🤝 Stakeholder Agreement", f"{alignment_data['component_scores']['stakeholder_agreement']:.0f}%")
    
    with col4:
        st.metric("📅 Timeline Consistency", f"{alignment_data['component_scores']['timeline_consistency']:.0f}%")
    
    # Alert
    st.markdown(f'<div class="alert-box alert-warning">⚠️ {alignment_data["alert"]}</div>', unsafe_allow_html=True)
    
    # Conflicts
    if alignment_data['conflicts']:
        st.markdown("### ⚔️ Detected Conflicts")
        for conflict in alignment_data['conflicts']:
            with st.expander(f"{conflict['type'].replace('_', ' ').title()}", expanded=True):
                st.markdown(f"**Description:** {conflict['description']}")
                st.markdown(f"**Severity:** {conflict['severity'].upper()}")
                st.markdown(f"**Recommendation:** {conflict['recommendation']}")

if __name__ == "__main__":
    main()
