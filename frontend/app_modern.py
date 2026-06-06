"""
ReqMind AI - Modern SaaS Dashboard
Clean, Light, Minimal Design (Uizard Style)
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time
from io import BytesIO
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

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
if 'gmail_syncing' not in st.session_state:
    st.session_state.gmail_syncing = False
if 'slack_syncing' not in st.session_state:
    st.session_state.slack_syncing = False
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Sample datasets
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
John (PM): Let's keep it simple for now."""


# Modern Light Theme CSS - Uizard Style
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Light Background */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Sidebar - Minimal Clean */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        padding: 0.5rem 0;
    }
    
    /* Logo Section */
    .logo-section {
        text-align: center;
        padding: 1.5rem 1rem 2rem 1rem;
        margin-bottom: 1rem;
    }
    
    .logo-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .logo-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E293B;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .logo-subtitle {
        font-size: 0.875rem;
        color: #64748B;
        font-weight: 500;
        margin-top: 0.25rem;
    }
    
    /* Navigation Buttons */
    .stButton > button {
        width: 100%;
        background-color: transparent;
        color: #64748B;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 500;
        font-size: 0.9375rem;
        text-align: left;
        transition: all 0.2s ease;
        margin: 0.125rem 0;
        box-shadow: none;
    }
    
    .stButton > button:hover {
        background-color: #F1F5F9;
        color: #6366F1;
    }
    
    /* White Cards */
    .card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
        border: 1px solid #F1F5F9;
    }
    
    .card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #F1F5F9;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E293B;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .metric-value-accent {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6366F1;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .metric-subtitle {
        font-size: 0.8125rem;
        color: #94A3B8;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Status Badges - Clean Pills */
    .badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8125rem;
        letter-spacing: 0.3px;
    }
    
    .badge-connected {
        background-color: #DCFCE7;
        color: #166534;
    }
    
    .badge-disconnected {
        background-color: #F1F5F9;
        color: #64748B;
    }
    
    .badge-syncing {
        background-color: #DBEAFE;
        color: #1E40AF;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Risk Badges */
    .risk-badge {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .risk-high {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 2px solid #FCA5A5;
    }
    
    .risk-medium {
        background-color: #FEF3C7;
        color: #92400E;
        border: 2px solid #FCD34D;
    }
    
    .risk-low {
        background-color: #DCFCE7;
        color: #166534;
        border: 2px solid #86EFAC;
    }
    
    /* Gauge Display */
    .gauge-container {
        text-align: center;
        padding: 2rem;
    }
    
    .gauge-score {
        font-size: 5rem;
        font-weight: 800;
        color: #6366F1;
        line-height: 1;
    }
    
    .gauge-label {
        font-size: 0.875rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    /* Integration Cards */
    .integration-card {
        background-color: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.2s ease;
    }
    
    .integration-card:hover {
        border-color: #C7D2FE;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    }
    
    .integration-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }
    
    .integration-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 0.5rem;
    }
    
    .integration-description {
        font-size: 0.875rem;
        color: #64748B;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    
    /* Primary Buttons */
    .btn-primary {
        background-color: #6366F1;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        font-size: 0.9375rem;
        box-shadow: 0 1px 3px rgba(99, 102, 241, 0.3);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .btn-primary:hover {
        background-color: #4F46E5;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        transform: translateY(-1px);
    }
    
    .btn-secondary {
        background-color: #F1F5F9;
        color: #475569;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .btn-secondary:hover {
        background-color: #E2E8F0;
        border-color: #CBD5E1;
    }
    
    /* Alert Cards */
    .alert-card {
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        border-left: 4px solid;
        font-weight: 500;
        font-size: 0.9375rem;
    }
    
    .alert-high {
        background-color: #FEF2F2;
        border-color: #EF4444;
        color: #991B1B;
    }
    
    .alert-medium {
        background-color: #FFFBEB;
        border-color: #F59E0B;
        color: #92400E;
    }
    
    .alert-low {
        background-color: #F0FDF4;
        border-color: #10B981;
        color: #166534;
    }
    
    /* Page Headers */
    .page-header {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.25rem;
    }
    
    .page-subtitle {
        font-size: 1rem;
        color: #64748B;
        font-weight: 400;
    }
    
    /* Conflict Cards */
    .conflict-card {
        background-color: #FFFFFF;
        border: 1px solid #FCA5A5;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        transition: all 0.2s ease;
    }
    
    .conflict-card:hover {
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
    }
    
    /* Text Styles */
    h1, h2, h3, h4, h5, h6 {
        color: #1E293B !important;
        font-weight: 600;
    }
    
    p, span, div, label {
        color: #475569 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }
    
    /* Divider */
    hr {
        border-color: #E2E8F0;
        margin: 1.5rem 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #F8FAFC;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        color: #1E293B !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #F1F5F9;
        border-color: #CBD5E1;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        color: #1E293B;
        font-size: 0.9375rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366F1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background-color: #6366F1;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: #6366F1;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Chart Container */
    .chart-container {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #F1F5F9;
    }
    
    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-connected {
        background-color: #10B981;
    }
    
    .status-disconnected {
        background-color: #94A3B8;
    }
    
    .status-syncing {
        background-color: #3B82F6;
        animation: pulse 2s infinite;
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
    """Simulate OAuth connection flow."""
    progress_text = f"Connecting to {service_name}..."
    progress_bar = st.progress(0, text=progress_text)
    
    for i in range(100):
        time.sleep(0.015)
        progress_bar.progress(i + 1, text=progress_text)
    
    st.success(f"✓ {service_name} connected successfully!")
    time.sleep(0.8)
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

def generate_brd_pdf(brd_data, alignment_data):
    """Generate PDF document for BRD."""
    if not PDF_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#6366F1'),
        spaceAfter=10,
        spaceBefore=20
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )
    
    # Title
    elements.append(Paragraph("Business Requirements Document", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Project Name
    elements.append(Paragraph(f"<b>Project:</b> {brd_data['projectName']}", body_style))
    elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Alignment Score Section
    elements.append(Paragraph("Alignment Analysis", heading_style))
    score = alignment_data['alignment_score']
    risk = alignment_data['risk_level']
    elements.append(Paragraph(f"<b>Alignment Score:</b> {score:.0f}/100", body_style))
    elements.append(Paragraph(f"<b>Risk Level:</b> {risk}", body_style))
    elements.append(Paragraph(f"<b>Alert:</b> {alignment_data['alert']}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(Paragraph(brd_data['executiveSummary'], body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Business Objectives
    elements.append(Paragraph("Business Objectives", heading_style))
    for obj in brd_data['businessObjectives']:
        elements.append(Paragraph(f"• {obj}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Requirements
    elements.append(Paragraph("Requirements", heading_style))
    for req in brd_data['requirements']:
        req_text = f"<b>{req['id']}</b> [{req['priority']}]: {req['description']}"
        elements.append(Paragraph(req_text, body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Stakeholders
    elements.append(Paragraph("Stakeholders", heading_style))
    for stakeholder in brd_data['stakeholders']:
        elements.append(Paragraph(f"• <b>{stakeholder['name']}</b> - {stakeholder['role']}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Conflicts
    if alignment_data['conflicts']:
        elements.append(Paragraph("Detected Conflicts", heading_style))
        for i, conflict in enumerate(alignment_data['conflicts'], 1):
            conflict_text = f"<b>Conflict {i}:</b> {conflict['type'].replace('_', ' ').title()}<br/>"
            conflict_text += f"<b>Severity:</b> {conflict['severity'].upper()}<br/>"
            conflict_text += f"<b>Description:</b> {conflict['description']}<br/>"
            conflict_text += f"<b>Recommendation:</b> {conflict['recommendation']}"
            elements.append(Paragraph(conflict_text, body_style))
            elements.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def render_sidebar():
    """Render minimal clean sidebar."""
    with st.sidebar:
        # Logo Section
        st.markdown("""
        <div class="logo-section">
            <div class="logo-icon">🎯</div>
            <div class="logo-title">ReqMind AI</div>
            <div class="logo-subtitle">Alignment Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Navigation
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
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Status
        api_status = check_api_status()
        status_class = "status-connected" if api_status else "status-disconnected"
        status_text = "Connected" if api_status else "Disconnected"
        
        st.markdown(f"""
        <div style="padding: 0.75rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.5rem;">API STATUS</div>
            <div>
                <span class="status-indicator {status_class}"></span>
                <span style="font-size: 0.875rem; font-weight: 600; color: #475569;">{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_dashboard():
    """Render clean modern dashboard."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Dashboard</div>
        <div class="page-subtitle">Real-time project alignment overview</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get latest data
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
    
    # Top Row - 4 Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Alignment Score</div>
            <div class="metric-value-accent">{latest_score:.0f}</div>
            <div class="metric-subtitle">out of 100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        risk_class = f"risk-{latest_risk.lower()}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Risk Level</div>
            <div class="risk-badge {risk_class}">{latest_risk}</div>
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Early Warning Alert
    st.markdown("### Early Warning Alert")
    
    if st.session_state.current_analysis:
        alert_msg = st.session_state.current_analysis['alignment_analysis']['alert']
        alert_class = f"alert-{latest_risk.lower()}"
        st.markdown(f"""
        <div class="alert-card {alert_class}">
            <strong>{latest_risk} RISK:</strong> {alert_msg}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-card alert-low">
            <strong>System Ready:</strong> No analysis performed yet. Connect data sources to begin.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two Column Layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Stakeholder Disagreement")
        st.markdown(f"""
        <div class="card">
            <p style="margin: 0.5rem 0;"><strong>Status:</strong> Monitoring</p>
            <p style="margin: 0.5rem 0;"><strong>Detected Issues:</strong> {conflict_count}</p>
            <p style="margin: 0.5rem 0;"><strong>Last Check:</strong> 5 minutes ago</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Timeline Volatility")
        st.markdown(f"""
        <div class="card">
            <p style="margin: 0.5rem 0;"><strong>Consistency:</strong> 85%</p>
            <p style="margin: 0.5rem 0;"><strong>Mismatches:</strong> {timeline_issues}</p>
            <p style="margin: 0.5rem 0;"><strong>Average Delay:</strong> 5 days</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Run New Analysis", use_container_width=True, type="primary"):
            st.session_state.page = 'data_sources'
            st.rerun()


def render_data_sources():
    """Render data sources page with integration cards."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Data Sources</div>
        <div class="page-subtitle">Connect your communication platforms</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Integration Cards
    col1, col2 = st.columns(2)
    
    with col1:
        # Gmail Integration
        st.markdown("""
        <div class="integration-card">
            <div class="integration-icon">📧</div>
            <div class="integration-title">Gmail</div>
            <div class="integration-description">
                Sync project emails for requirement and timeline analysis
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.gmail_connected:
            if st.session_state.gmail_syncing:
                st.markdown('<span class="badge badge-syncing">⟳ Syncing</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge badge-connected">✓ Connected</span>', unsafe_allow_html=True)
            
            if st.button("Disconnect", key="disconnect_gmail"):
                st.session_state.gmail_connected = False
                st.session_state.gmail_syncing = False
                st.rerun()
        else:
            st.markdown('<span class="badge badge-disconnected">○ Disconnected</span>', unsafe_allow_html=True)
            if st.button("Connect Gmail", key="connect_gmail", use_container_width=True):
                simulate_oauth_connection("Gmail")
                st.session_state.gmail_connected = True
                st.session_state.gmail_syncing = True
                time.sleep(1)
                st.session_state.gmail_syncing = False
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Meetings
        st.markdown("""
        <div class="integration-card">
            <div class="integration-icon">🎤</div>
            <div class="integration-title">Meeting Transcripts</div>
            <div class="integration-description">
                Upload transcripts or connect Zoom/Google Meet
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.meetings_connected:
            st.markdown('<span class="badge badge-connected">✓ Connected</span>', unsafe_allow_html=True)
            if st.button("Disconnect", key="disconnect_meetings"):
                st.session_state.meetings_connected = False
                st.rerun()
        else:
            uploaded_file = st.file_uploader("Upload Transcript", type=['txt', 'pdf'], key="transcript_upload", label_visibility="collapsed")
            if uploaded_file:
                st.success("✓ Transcript uploaded!")
                st.session_state.meetings_connected = True
            
            if st.button("Connect Zoom/Meet", key="connect_meetings", use_container_width=True):
                simulate_oauth_connection("Meeting Platform")
                st.session_state.meetings_connected = True
                st.rerun()
    
    with col2:
        # Slack Integration
        st.markdown("""
        <div class="integration-card">
            <div class="integration-icon">💬</div>
            <div class="integration-title">Slack</div>
            <div class="integration-description">
                Analyze stakeholder discussions across channels
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.slack_connected:
            if st.session_state.slack_syncing:
                st.markdown('<span class="badge badge-syncing">⟳ Syncing</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge badge-connected">✓ Connected</span>', unsafe_allow_html=True)
            
            if st.button("Disconnect", key="disconnect_slack"):
                st.session_state.slack_connected = False
                st.session_state.slack_syncing = False
                st.rerun()
        else:
            st.markdown('<span class="badge badge-disconnected">○ Disconnected</span>', unsafe_allow_html=True)
            if st.button("Connect Slack", key="connect_slack", use_container_width=True):
                simulate_oauth_connection("Slack")
                st.session_state.slack_connected = True
                st.session_state.slack_syncing = True
                time.sleep(1)
                st.session_state.slack_syncing = False
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Demo Mode
        st.markdown("""
        <div class="integration-card">
            <div class="integration-icon">🎯</div>
            <div class="integration-title">Demo Mode</div>
            <div class="integration-description">
                Load sample data for quick testing
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Load Sample Data", key="load_sample", use_container_width=True):
            with st.spinner("Loading sample data..."):
                time.sleep(1)
                st.session_state.gmail_connected = True
                st.session_state.slack_connected = True
                st.session_state.meetings_connected = True
                st.success("✓ Sample data loaded!")
                time.sleep(0.8)
                st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Analyze Button
    if st.session_state.gmail_connected or st.session_state.slack_connected or st.session_state.meetings_connected:
        st.markdown("""
        <div class="alert-card alert-low">
            <strong>Ready to Analyze:</strong> Data sources connected. Click below to run alignment analysis.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Analyze Alignment", key="analyze_now", use_container_width=True, type="primary"):
                email_data = SAMPLE_GMAIL_DATA if st.session_state.gmail_connected else ""
                slack_data = SAMPLE_SLACK_DATA if st.session_state.slack_connected else ""
                meeting_data = SAMPLE_MEETING_DATA if st.session_state.meetings_connected else ""
                
                with st.spinner("Analyzing alignment..."):
                    try:
                        result = call_alignment_api(
                            "Connected Project",
                            email_data,
                            slack_data,
                            meeting_data
                        )
                        st.session_state.current_analysis = result
                        st.session_state.analysis_history.append({
                            'timestamp': datetime.now(),
                            'project': "Connected Project",
                            'result': result
                        })
                        st.success("✓ Analysis complete!")
                        time.sleep(0.8)
                        st.session_state.page = 'analysis'
                        st.rerun()
                    except Exception as e:
                        st.error(f"✗ Analysis failed: {str(e)}")


def render_analysis():
    """Render alignment analysis page."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Alignment Analysis</div>
        <div class="page-subtitle">Detailed conflict and alignment report</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.current_analysis:
        st.markdown("""
        <div class="alert-card alert-medium">
            <strong>No Analysis Available:</strong> Please run an analysis from the Data Sources page.
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
    
    # Large Alignment Score Gauge
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <div class="risk-badge {risk_class}">{risk_level} Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Alert Message
    alert_msg = alignment_data['alert']
    alert_class = f"alert-{risk_level.lower()}"
    st.markdown(f"""
    <div class="alert-card {alert_class}">
        <strong>{risk_level} RISK ALERT:</strong> {alert_msg}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Conflict List
    st.markdown("### Conflict List")
    conflicts = alignment_data['conflicts']
    
    if conflicts:
        for i, conflict in enumerate(conflicts, 1):
            severity_colors = {
                'high': '#FEE2E2',
                'medium': '#FEF3C7',
                'low': '#DCFCE7'
            }
            bg_color = severity_colors.get(conflict['severity'], '#F8FAFC')
            
            with st.expander(f"Conflict {i}: {conflict['type'].replace('_', ' ').title()}", expanded=True):
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0.5rem 0;"><strong>Type:</strong> {conflict['type'].replace('_', ' ').title()}</p>
                    <p style="margin: 0.5rem 0;"><strong>Severity:</strong> {conflict['severity'].upper()}</p>
                    <p style="margin: 0.5rem 0;"><strong>Description:</strong> {conflict['description']}</p>
                    <p style="margin: 0.5rem 0;"><strong>Sources:</strong> {', '.join(conflict['sources'])}</p>
                    <p style="margin: 0.5rem 0;"><strong>💡 Recommendation:</strong> {conflict['recommendation']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-card alert-low">
            <strong>No Conflicts:</strong> All stakeholders are aligned.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Requirement Volatility
    st.markdown("### Requirement Volatility")
    if alignment_data.get('requirement_volatility'):
        volatility = alignment_data['requirement_volatility']
        st.markdown(f"""
        <div class="card">
            <p style="margin: 0.5rem 0;"><strong>Total Changes:</strong> {volatility.get('total_changes', 0)}</p>
            <p style="margin: 0.5rem 0;"><strong>Trend:</strong> {volatility.get('trend', 'Stable')}</p>
            <p style="margin: 0.5rem 0;"><strong>Impact:</strong> {volatility.get('impact', 'Low')}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        component_scores = alignment_data['component_scores']
        stability_score = component_scores.get('requirement_stability', 100)
        st.markdown(f"""
        <div class="card">
            <p style="margin: 0.5rem 0;"><strong>Stability Score:</strong> {stability_score:.0f}%</p>
            <p style="margin: 0.5rem 0;"><strong>Status:</strong> {'Stable' if stability_score > 80 else 'Volatile'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Decision Reversals
    st.markdown("### Decision Reversals")
    if alignment_data.get('decision_reversals'):
        for reversal in alignment_data['decision_reversals']:
            st.markdown(f"""
            <div class="card">
                <p style="margin: 0.5rem 0;"><strong>Decision:</strong> {reversal.get('decision', 'N/A')}</p>
                <p style="margin: 0.5rem 0;"><strong>Impact:</strong> {reversal.get('impact', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        component_scores = alignment_data['component_scores']
        volatility_score = component_scores.get('decision_volatility', 100)
        st.markdown(f"""
        <div class="card">
            <p style="margin: 0.5rem 0;"><strong>Volatility Score:</strong> {volatility_score:.0f}%</p>
            <p style="margin: 0.5rem 0;"><strong>Status:</strong> {'Low' if volatility_score > 80 else 'High'} volatility</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # BRD Viewer Section
    st.markdown("### Business Requirements Document")
    with st.expander("📄 View Complete BRD", expanded=False):
        st.markdown(f"**Project Name:** {brd_data['projectName']}")
        st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        st.markdown("---")
        
        st.markdown("**Executive Summary**")
        st.write(brd_data['executiveSummary'])
        
        st.markdown("**Business Objectives**")
        for obj in brd_data['businessObjectives']:
            st.markdown(f"• {obj}")
        
        st.markdown("**Requirements**")
        for req in brd_data['requirements']:
            priority_colors = {'High': '🔴', 'Medium': '🟠', 'Low': '🟢'}
            priority_icon = priority_colors.get(req['priority'], '⚪')
            st.markdown(f"{priority_icon} **{req['id']}** [{req['priority']}]: {req['description']}")
        
        st.markdown("**Stakeholders**")
        for stakeholder in brd_data['stakeholders']:
            st.markdown(f"• **{stakeholder['name']}** - {stakeholder['role']}")
        
        if 'timeline' in brd_data:
            st.markdown(f"**Timeline:** {brd_data['timeline']}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # PDF Download
        if PDF_AVAILABLE:
            pdf_buffer = generate_brd_pdf(brd_data, alignment_data)
            if pdf_buffer:
                st.download_button(
                    label="📥 Download BRD (PDF)",
                    data=pdf_buffer,
                    file_name=f"reqmind_brd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("Install reportlab for PDF export: pip install reportlab")
    
    with col2:
        # JSON Download (backup)
        json_str = json.dumps(result, indent=2)
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json_str,
            file_name=f"reqmind_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )


def render_brd_history():
    """Render BRD history page."""
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">BRD History</div>
        <div class="page-subtitle">Past analysis reports</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.analysis_history:
        st.markdown("""
        <div class="alert-card alert-medium">
            <strong>No History:</strong> Run your first analysis to see results here.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Data Sources", use_container_width=True):
                st.session_state.page = 'data_sources'
                st.rerun()
        return
    
    st.markdown(f"**Total Analyses:** {len(st.session_state.analysis_history)}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display history
    for i, entry in enumerate(reversed(st.session_state.analysis_history)):
        alignment_score = entry['result']['alignment_analysis']['alignment_score']
        risk_level = entry['result']['alignment_analysis']['risk_level']
        conflicts = len(entry['result']['alignment_analysis']['conflicts'])
        timestamp = entry['timestamp'].strftime('%Y-%m-%d %H:%M')
        
        risk_colors = {'HIGH': '#991B1B', 'MEDIUM': '#92400E', 'LOW': '#166534'}
        risk_color = risk_colors.get(risk_level, '#475569')
        
        with st.expander(f"{entry['project']} - {timestamp}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.25rem;">SCORE</div>
                    <div style="font-size: 2rem; font-weight: 700; color: {risk_color};">{alignment_score:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.25rem;">RISK</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {risk_color};">{risk_level}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.25rem;">CONFLICTS</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #1E293B;">{conflicts}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if st.button("View Details", key=f"view_{i}", use_container_width=True):
                    st.session_state.current_analysis = entry['result']
                    st.session_state.page = 'analysis'
                    st.rerun()


def main():
    """Main application."""
    render_sidebar()
    
    # Route to pages
    if st.session_state.page == 'dashboard':
        render_dashboard()
    elif st.session_state.page == 'data_sources':
        render_data_sources()
    elif st.session_state.page == 'analysis':
        render_analysis()
    elif st.session_state.page == 'brd_history':
        render_brd_history()


if __name__ == "__main__":
    main()
