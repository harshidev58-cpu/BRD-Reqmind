"""
ReqMind AI - Enterprise SaaS Interface
Modern AI-powered Alignment Intelligence System
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time

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
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Sample datasets for simulation
SAMPLE_GMAIL_DATA = """From: john.pm@company.com
Subject: Q1 Project Deadline

Team, we need to deliver this by March 30 for the Q1 release. This is critical and urgent.

From: client@external.com  
Subject: Re: Project Timeline

Actually, we need delivery by April 10 to accommodate our internal review process."""

SAMPLE_SLACK_DATA = """#project-alpha
@john.pm: Simple MVP approach - keep it basic
@sarah.dev: I disagree, we need a comprehensive solution with all features
@mike.lead: The scope keeps changing every week, causing confusion"""


# Custom CSS for modern SaaS design
st.markdown("""
<style>
    /* Dark theme with gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0c4a6e 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    /* Card styling */
    .metric-card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(59, 130, 246, 0.4);
        border-color: rgba(59, 130, 246, 0.6);
    }
    
    /* Integration card */
    .integration-card {
        background: rgba(30, 41, 59, 0.6);
        border: 2px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .integration-card:hover {
        border-color: rgba(59, 130, 246, 0.5);
        background: rgba(30, 41, 59, 0.8);
    }
    
    /* Status badges */
    .status-connected {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    .status-disconnected {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
    }
    
    /* Risk level badges */
    .risk-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.5);
        animation: pulse 2s infinite;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(245, 158, 11, 0.5);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.5);
    }
    
    /* Gauge styling */
    .gauge-container {
        text-align: center;
        padding: 2rem;
    }
    
    .gauge-score {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.6);
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar menu items */
    .sidebar-item {
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #94a3b8;
    }
    
    .sidebar-item:hover {
        background: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
    }
    
    .sidebar-item-active {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def check_api_status():
    """Check if backend API is reachable."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def simulate_oauth_connection(service_name):
    """Simulate OAuth connection flow."""
    with st.spinner(f"🔄 Connecting to {service_name}..."):
        time.sleep(2)  # Simulate OAuth flow
        st.success(f"✅ {service_name} connected successfully!")
        time.sleep(1)

def call_alignment_api(project_name, email_text, slack_text, meeting_text, instructions=None):
    """Call backend API for alignment analysis with optional instructions."""
    if instructions:
        # Use new context endpoint with Gemini instructions
        payload = {
            "instructions": instructions,
            "data": {
                "emails": [{"subject": "Project Data", "body": email_text, "sender": "auto@reqmind.ai", "date": datetime.now().isoformat()}] if email_text else [],
                "slack_messages": [{"channel": "#project", "user": "auto", "text": slack_text, "timestamp": datetime.now().isoformat()}] if slack_text else [],
                "meetings": [{"transcript": meeting_text, "topic": "Project Meeting", "speakers": ["Team"]}] if meeting_text else []
            }
        }
        
        response = requests.post(
            f"{API_BASE_URL}/generate_brd_with_context",
            json=payload,
            timeout=30
        )
    else:
        # Use standard endpoint without instructions
        payload = {
            "projectName": project_name,
            "emailText": email_text if email_text else None,
            "slackText": slack_text if slack_text else None,
            "meetingText": meeting_text if meeting_text else None
        }
        
        response = requests.post(
            f"{API_BASE_URL}/generate_brd_with_alignment",
            json=payload,
            timeout=30
        )
    
    response.raise_for_status()
    return response.json()

def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 2rem 0;">
            <h1 style="font-size: 2rem; margin: 0;">🎯 ReqMind AI</h1>
            <p style="color: #64748b; margin: 0.5rem 0 0 0;">Alignment Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### Navigation")
        
        menu_items = [
            ("dashboard", "📊 Dashboard", "dashboard"),
            ("data_sources", "🔌 Data Sources", "data_sources"),
            ("analysis", "🎯 Alignment Analysis", "analysis"),
            ("brd_history", "📄 BRD History", "brd_history"),
            ("settings", "⚙️ Settings", "settings")
        ]
        
        for key, label, page in menu_items:
            if st.button(label, key=key, use_container_width=True):
                st.session_state.page = page
                st.rerun()
        
        st.markdown("---")
        
        # API Status
        st.markdown("### 🔌 System Status")
        api_status = check_api_status()
        if api_status:
            st.markdown('<div class="status-connected">✅ API Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-disconnected">❌ API Disconnected</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("© 2024 ReqMind AI | v2.0")


def render_dashboard():
    """Render the main dashboard page."""
    st.markdown("# 📊 Dashboard")
    st.markdown("### Welcome to ReqMind AI Alignment Intelligence")
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #64748b; margin: 0;">Alignment Score</h4>
            <div class="gauge-score">85</div>
            <p style="color: #64748b; margin: 0;">Last Analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #64748b; margin: 0;">Risk Level</h4>
            <div class="risk-low" style="margin: 1rem 0; font-size: 1.2rem;">LOW</div>
            <p style="color: #64748b; margin: 0;">Stable</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #64748b; margin: 0;">Active Conflicts</h4>
            <div class="gauge-score" style="font-size: 3rem;">2</div>
            <p style="color: #64748b; margin: 0;">Detected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #64748b; margin: 0;">Timeline Issues</h4>
            <div class="gauge-score" style="font-size: 3rem;">1</div>
            <p style="color: #64748b; margin: 0;">Mismatch</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent activity section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Recent Activity")
        st.markdown("""
        <div class="metric-card">
            <p><strong>Last Analysis:</strong> 2 hours ago</p>
            <p><strong>Project:</strong> Q1 Platform Release</p>
            <p><strong>Sources:</strong> Gmail, Slack, Meeting Transcripts</p>
            <p><strong>Result:</strong> <span style="color: #10b981;">✅ Low Risk</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔌 Connected Sources")
        if st.session_state.gmail_connected:
            st.markdown('<div class="status-connected">📧 Gmail</div>', unsafe_allow_html=True)
        if st.session_state.slack_connected:
            st.markdown('<div class="status-connected">💬 Slack</div>', unsafe_allow_html=True)
        
        if not st.session_state.gmail_connected and not st.session_state.slack_connected:
            st.info("No sources connected yet")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run New Analysis", use_container_width=True, type="primary"):
            st.session_state.page = 'data_sources'
            st.rerun()


def render_data_sources():
    """Render the data sources page with integration cards."""
    st.markdown("# 🔌 Data Sources")
    st.markdown("### Connected Communication Sources")
    st.caption("ReqMind automatically collects project communication from your tools")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Integration cards in grid
    col1, col2 = st.columns(2)
    
    with col1:
        # Gmail Card
        st.markdown("""
        <div class="integration-card">
            <h3>📧 Gmail Integration</h3>
            <p style="color: #94a3b8;">Sync project emails for requirement and timeline analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.gmail_connected:
            st.markdown('<div class="status-connected">✅ Connected</div>', unsafe_allow_html=True)
            st.caption("Automatically collecting emails...")
            if st.button("Disconnect Gmail", key="disconnect_gmail"):
                st.session_state.gmail_connected = False
                st.rerun()
        else:
            st.markdown('<div class="status-disconnected">❌ Disconnected</div>', unsafe_allow_html=True)
            if st.button("Connect Gmail", key="connect_gmail", use_container_width=True):
                simulate_oauth_connection("Gmail")
                st.session_state.gmail_connected = True
                st.rerun()
    
    with col2:
        # Slack Card
        st.markdown("""
        <div class="integration-card">
            <h3>💬 Slack Integration</h3>
            <p style="color: #94a3b8;">Analyze stakeholder discussions across channels</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.slack_connected:
            st.markdown('<div class="status-connected">✅ Connected</div>', unsafe_allow_html=True)
            st.caption("Monitoring #project channels...")
            if st.button("Disconnect Slack", key="disconnect_slack"):
                st.session_state.slack_connected = False
                st.rerun()
        else:
            st.markdown('<div class="status-disconnected">❌ Disconnected</div>', unsafe_allow_html=True)
            if st.button("Connect Slack", key="connect_slack", use_container_width=True):
                simulate_oauth_connection("Slack")
                st.session_state.slack_connected = True
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Meeting transcripts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="integration-card">
            <h3>🎤 Meeting Transcripts</h3>
            <p style="color: #94a3b8;">Upload or connect meeting platforms</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Transcript", type=['txt', 'pdf'], key="transcript_upload")
        if uploaded_file:
            st.success("✅ Transcript uploaded successfully!")
    
    with col2:
        st.markdown("""
        <div class="integration-card">
            <h3>🎯 Demo Mode</h3>
            <p style="color: #94a3b8;">Quick analysis with sample data</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Load Sample Dataset", use_container_width=True):
            st.session_state.gmail_connected = True
            st.session_state.slack_connected = True
            st.success("✅ Sample data loaded from Gmail and Slack!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Auto-analysis section
    if st.session_state.gmail_connected or st.session_state.slack_connected:
        st.markdown("### 🤖 Auto-Ingestion Active")
        st.info("✨ Data automatically collected from connected sources")
        
        # Gemini Instructions Section
        st.markdown("### ✨ AI Instructions (Gemini-Powered)")
        st.markdown("""
        <div class="integration-card">
            <p style="color: #94a3b8;">
                Use natural language to guide the analysis. Tell the system what to focus on, 
                what to ignore, and what to prioritize.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        instructions = st.text_area(
            "Project Instructions (Optional)",
            placeholder="Example: Focus on MVP features only, ignore marketing discussions, prioritize mobile functionality, client deadline is June 2024",
            height=100,
            help="Gemini AI will convert your instructions into structured constraints for intelligent filtering"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Analyze Alignment Now", use_container_width=True, type="primary"):
                # Collect data from connected sources
                email_data = SAMPLE_GMAIL_DATA if st.session_state.gmail_connected else ""
                slack_data = SAMPLE_SLACK_DATA if st.session_state.slack_connected else ""
                
                with st.spinner("🔄 Analyzing alignment across all sources..."):
                    try:
                        result = call_alignment_api(
                            "Auto-Collected Project",
                            email_data,
                            slack_data,
                            "",
                            instructions=instructions if instructions.strip() else None
                        )
                        st.session_state.current_analysis = result
                        st.session_state.analysis_history.append({
                            'timestamp': datetime.now(),
                            'project': "Auto-Collected Project",
                            'result': result
                        })
                        st.session_state.page = 'analysis'
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")


def render_analysis():
    """Render the alignment analysis results page."""
    st.markdown("# 🎯 Alignment Analysis")
    
    if not st.session_state.current_analysis:
        st.info("No analysis available. Please run an analysis from the Data Sources page.")
        if st.button("Go to Data Sources"):
            st.session_state.page = 'data_sources'
            st.rerun()
        return
    
    result = st.session_state.current_analysis
    alignment_data = result['alignment_analysis']
    brd_data = result['brd']
    
    # Alignment Score Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        score = alignment_data['alignment_score']
        st.markdown(f"""
        <div class="gauge-container">
            <h3 style="color: #64748b;">Alignment Score</h3>
            <div class="gauge-score">{score:.0f}</div>
            <p style="color: #94a3b8;">out of 100</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Risk badge
    risk_level = alignment_data['risk_level']
    risk_class = f"risk-{risk_level.lower()}"
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div class="{risk_class}">⚠️ {risk_level} RISK</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alert message
    st.markdown("### 🚨 Alert Status")
    if risk_level == 'HIGH':
        st.error(f"**{alignment_data['alert']}**")
    elif risk_level == 'MEDIUM':
        st.warning(f"**{alignment_data['alert']}**")
    else:
        st.success(f"**{alignment_data['alert']}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Insight cards
    st.markdown("### 📊 Insight Cards")
    col1, col2, col3, col4 = st.columns(4)
    
    component_scores = alignment_data['component_scores']
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🤝 Stakeholder Agreement</h4>
            <div class="gauge-score" style="font-size: 2.5rem;">{component_scores['stakeholder_agreement']:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📅 Timeline Consistency</h4>
            <div class="gauge-score" style="font-size: 2.5rem;">{component_scores['timeline_consistency']:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📋 Requirement Stability</h4>
            <div class="gauge-score" style="font-size: 2.5rem;">{component_scores['requirement_stability']:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🔄 Decision Volatility</h4>
            <div class="gauge-score" style="font-size: 2.5rem;">{component_scores['decision_volatility']:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Conflict details
    st.markdown("### ⚔️ Conflict Details")
    conflicts = alignment_data['conflicts']
    
    if conflicts:
        for i, conflict in enumerate(conflicts, 1):
            with st.expander(f"Conflict {i}: {conflict['type'].replace('_', ' ').title()}", expanded=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Description:** {conflict['description']}")
                    st.markdown(f"**Sources:** {', '.join(conflict['sources'])}")
                    st.markdown(f"**💡 Recommendation:** {conflict['recommendation']}")
                with col2:
                    severity_emoji = {'high': '🔴', 'medium': '🟠', 'low': '🟢'}
                    st.markdown(f"**Severity:** {severity_emoji.get(conflict['severity'], '⚪')} {conflict['severity'].upper()}")
    else:
        st.success("✅ No conflicts detected!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Timeline mismatches
    if alignment_data['timeline_mismatches']:
        st.markdown("### 📅 Timeline Mismatches")
        for mismatch in alignment_data['timeline_mismatches']:
            st.warning(f"**{mismatch['description']}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ingestion Summary (if available from context endpoint)
    if 'ingestion_summary' in result and result['ingestion_summary']:
        st.markdown("### 📊 Ingestion Summary")
        summary = result['ingestion_summary']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📧 Emails</h4>
                <div class="gauge-score" style="font-size: 2rem;">{summary.get('emails_used', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💬 Slack Messages</h4>
                <div class="gauge-score" style="font-size: 2rem;">{summary.get('slack_messages_used', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎤 Meetings</h4>
                <div class="gauge-score" style="font-size: 2rem;">{summary.get('meetings_used', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h4>⏱️ Processing Time</h4>
                <div class="gauge-score" style="font-size: 2rem;">{summary.get('processing_time_seconds', 0):.1f}s</div>
            </div>
            """, unsafe_allow_html=True)
        
        if summary.get('total_chunks_processed', 0) > 0:
            st.info(f"📦 Large data was automatically chunked into {summary['total_chunks_processed']} parts for processing")
        
        if summary.get('sample_sources'):
            with st.expander("📋 View Sample Sources Used", expanded=False):
                for i, source in enumerate(summary['sample_sources'], 1):
                    st.markdown(f"**Source {i}:** {source.get('type', 'unknown').title()}")
                    if 'metadata' in source:
                        for key, value in source['metadata'].items():
                            st.markdown(f"- {key}: {value}")
                    st.markdown("---")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # BRD Viewer
    st.markdown("### 📄 Generated Business Requirements Document")
    with st.expander("View Complete BRD", expanded=False):
        st.markdown(f"**Project:** {brd_data['projectName']}")
        st.markdown(f"**Executive Summary:** {brd_data['executiveSummary']}")
        
        st.markdown("**Business Objectives:**")
        for obj in brd_data['businessObjectives']:
            st.markdown(f"- {obj}")
        
        st.markdown("**Requirements:**")
        for req in brd_data['requirements']:
            priority_emoji = {'High': '🔴', 'Medium': '🟠', 'Low': '🟢'}.get(req['priority'], '⚪')
            st.markdown(f"{priority_emoji} **{req['id']}**: {req['description']}")
        
        st.markdown("**Stakeholders:**")
        for stakeholder in brd_data['stakeholders']:
            st.markdown(f"- **{stakeholder['name']}** - {stakeholder['role']}")
    
    # Download button
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
    """Render the BRD history page."""
    st.markdown("# 📄 BRD History")
    st.markdown("### Analysis History")
    
    if not st.session_state.analysis_history:
        st.info("No analysis history yet. Run your first analysis to see results here.")
        if st.button("Go to Data Sources"):
            st.session_state.page = 'data_sources'
            st.rerun()
        return
    
    # Display history table
    for i, entry in enumerate(reversed(st.session_state.analysis_history)):
        alignment_score = entry['result']['alignment_analysis']['alignment_score']
        risk_level = entry['result']['alignment_analysis']['risk_level']
        
        with st.expander(f"{entry['project']} - {entry['timestamp'].strftime('%Y-%m-%d %H:%M')}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Alignment Score", f"{alignment_score:.0f}")
            with col2:
                risk_color = {'HIGH': '🔴', 'MEDIUM': '🟠', 'LOW': '🟢'}
                st.markdown(f"**Risk:** {risk_color[risk_level]} {risk_level}")
            with col3:
                conflicts = len(entry['result']['alignment_analysis']['conflicts'])
                st.metric("Conflicts", conflicts)
            with col4:
                if st.button("View Details", key=f"view_{i}"):
                    st.session_state.current_analysis = entry['result']
                    st.session_state.page = 'analysis'
                    st.rerun()

def render_settings():
    """Render the settings page."""
    st.markdown("# ⚙️ Settings")
    st.markdown("### System Configuration")
    
    st.markdown("#### API Configuration")
    st.text_input("Backend API URL", value=API_BASE_URL, disabled=True)
    
    st.markdown("#### Notification Settings")
    st.checkbox("Email alerts for HIGH risk", value=True)
    st.checkbox("Slack notifications", value=False)
    
    st.markdown("#### Analysis Settings")
    st.slider("Conflict sensitivity", 1, 10, 5)
    st.slider("Timeline tolerance (days)", 1, 30, 7)
    
    st.markdown("#### Data Management")
    if st.button("Clear Analysis History"):
        st.session_state.analysis_history = []
        st.success("✅ History cleared")
    
    if st.button("Reset All Connections"):
        st.session_state.gmail_connected = False
        st.session_state.slack_connected = False
        st.success("✅ All connections reset")

def main():
    """Main application function."""
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
