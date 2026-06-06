"""
ReqMind AI - Project Alignment Intelligence Dashboard
A professional Streamlit frontend for analyzing stakeholder communication alignment
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

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f1f1f;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .risk-high {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.5rem;
        text-align: center;
    }
    .risk-medium {
        background: linear-gradient(135deg, #ffa500 0%, #ffb733 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.5rem;
        text-align: center;
    }
    .risk-low {
        background: linear-gradient(135deg, #00cc66 0%, #00e676 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.5rem;
        text-align: center;
    }
    .alert-box {
        background: #fff3cd;
        border-left: 4px solid #ffa500;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .conflict-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff4b4b;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #00cc66;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = f"{API_BASE_URL}/generate_brd_with_alignment"

# Sample test data
SAMPLE_SCENARIO = """PM (Slack): We need delivery by March 30. This is critical for the Q1 release. The system must be simple and basic for MVP.

Client (Email): I need the delivery by April 10 at the latest. We have internal reviews that week. Actually, we need a comprehensive, advanced system with all features.

Developer (Meeting): Backend dependency may delay release. I disagree with the timeline - we need at least until May. The scope keeps changing every week, which is causing confusion."""

def check_api_status():
    """Check if the backend API is reachable."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def call_alignment_api(project_name, communication_text):
    """Call the backend API for alignment analysis."""
    # Parse communication text into channels (simple heuristic)
    lines = communication_text.strip().split('\n\n')
    
    email_text = ""
    slack_text = ""
    meeting_text = ""
    
    for line in lines:
        if 'email' in line.lower():
            email_text = line
        elif 'slack' in line.lower():
            slack_text = line
        elif 'meeting' in line.lower():
            meeting_text = line
        else:
            # Default to email if no channel specified
            if not email_text:
                email_text = line
            elif not slack_text:
                slack_text = line
            else:
                meeting_text = line
    
    # If still empty, use the whole text as email
    if not email_text and not slack_text and not meeting_text:
        email_text = communication_text
    
    payload = {
        "projectName": project_name,
        "emailText": email_text if email_text else None,
        "slackText": slack_text if slack_text else None,
        "meetingText": meeting_text if meeting_text else None
    }
    
    response = requests.post(API_ENDPOINT, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def render_sidebar():
    """Render the sidebar with project info and API status."""
    with st.sidebar:
        st.markdown("### 🎯 ReqMind AI")
        st.markdown("**Alignment Intelligence System**")
        st.markdown("---")
        
        # API Status
        st.markdown("### 🔌 API Status")
        api_status = check_api_status()
        if api_status:
            st.markdown('<div class="success-box">✅ Backend Connected</div>', unsafe_allow_html=True)
        else:
            st.error("❌ Backend Disconnected")
            st.caption("Make sure the backend is running at http://127.0.0.1:8000")
        
        st.markdown("---")
        
        # Project Info
        st.markdown("### 📊 About")
        st.markdown("""
        ReqMind AI analyzes stakeholder communication to:
        - Detect conflicts & disagreements
        - Identify timeline mismatches
        - Track requirement volatility
        - Assess project alignment risk
        - Generate structured BRDs
        """)
        
        st.markdown("---")
        st.markdown("### 🎨 Risk Levels")
        st.markdown("🔴 **HIGH** (< 70): Immediate action")
        st.markdown("🟠 **MEDIUM** (70-85): Monitor closely")
        st.markdown("🟢 **LOW** (> 85): Stable alignment")
        
        st.markdown("---")
        st.caption(f"© 2024 ReqMind AI | v1.0")

def render_metrics_row(alignment_data):
    """Render the top metrics row."""
    col1, col2, col3, col4 = st.columns(4)
    
    alignment_score = alignment_data['alignment_score']
    risk_level = alignment_data['risk_level']
    component_scores = alignment_data['component_scores']
    
    with col1:
        st.metric(
            label="🎯 Alignment Score",
            value=f"{alignment_score:.1f}",
            delta=f"{alignment_score - 70:.1f} from threshold"
        )
    
    with col2:
        risk_color = {
            'HIGH': 'risk-high',
            'MEDIUM': 'risk-medium',
            'LOW': 'risk-low'
        }[risk_level]
        st.markdown(f'<div class="{risk_color}">⚠️ {risk_level} RISK</div>', unsafe_allow_html=True)
    
    with col3:
        st.metric(
            label="🤝 Stakeholder Agreement",
            value=f"{component_scores['stakeholder_agreement']:.0f}%"
        )
    
    with col4:
        st.metric(
            label="📅 Timeline Consistency",
            value=f"{component_scores['timeline_consistency']:.0f}%"
        )

def render_alert_section(alert_message, risk_level):
    """Render the alert message section."""
    st.markdown("### 🚨 Alert Status")
    
    if risk_level == 'HIGH':
        st.error(f"**{alert_message}**")
    elif risk_level == 'MEDIUM':
        st.warning(f"**{alert_message}**")
    else:
        st.success(f"**{alert_message}**")

def render_conflicts_section(conflicts):
    """Render the conflicts insights section."""
    st.markdown("### ⚔️ Conflict Insights")
    
    if not conflicts:
        st.success("✅ No conflicts detected. Project alignment is good!")
        return
    
    for i, conflict in enumerate(conflicts, 1):
        with st.expander(f"Conflict {i}: {conflict['type'].replace('_', ' ').title()}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {conflict['description']}")
                st.markdown(f"**Sources:** {', '.join(conflict['sources'])}")
                st.markdown(f"**Recommendation:** {conflict['recommendation']}")
            
            with col2:
                severity_color = {
                    'high': '🔴',
                    'medium': '🟠',
                    'low': '🟢'
                }
                st.markdown(f"**Severity:** {severity_color.get(conflict['severity'], '⚪')} {conflict['severity'].upper()}")
                if conflict.get('entities_involved'):
                    st.markdown(f"**Entities:** {', '.join(conflict['entities_involved'])}")

def render_timeline_section(timeline_mismatches):
    """Render the timeline mismatch section."""
    st.markdown("### 📅 Timeline Analysis")
    
    if not timeline_mismatches:
        st.success("✅ No timeline mismatches detected.")
        return
    
    for mismatch in timeline_mismatches:
        st.warning(f"**{mismatch['description']}**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{mismatch['source1'].title()}:** {', '.join(mismatch['dates1'])}")
        with col2:
            st.markdown(f"**{mismatch['source2'].title()}:** {', '.join(mismatch['dates2'])}")

def render_volatility_section(volatility):
    """Render the requirement volatility section."""
    st.markdown("### 📊 Requirement Volatility")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Changes Detected", volatility['change_count'])
    
    with col2:
        st.metric("Stability Score", f"{volatility['stability_percentage']:.1f}%")
    
    with col3:
        st.metric("Total Requirements", volatility['total_requirements'])
    
    if volatility['change_sources']:
        st.caption(f"Changes detected in: {', '.join(volatility['change_sources'])}")

def render_stakeholders_section(brd_data):
    """Render the stakeholders section."""
    st.markdown("### 👥 Identified Stakeholders")
    
    stakeholders = brd_data.get('stakeholders', [])
    
    if not stakeholders:
        st.info("No stakeholders identified.")
        return
    
    cols = st.columns(min(len(stakeholders), 3))
    for i, stakeholder in enumerate(stakeholders):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{stakeholder['name']}</h4>
                <p style="color: #666;">{stakeholder['role']}</p>
            </div>
            """, unsafe_allow_html=True)

def render_brd_section(brd_data):
    """Render the BRD section."""
    st.markdown("### 📄 Generated Business Requirements Document")
    
    with st.expander("View Complete BRD", expanded=False):
        st.markdown(f"**Project Name:** {brd_data['projectName']}")
        
        st.markdown("#### Executive Summary")
        st.write(brd_data['executiveSummary'])
        
        st.markdown("#### Business Objectives")
        for obj in brd_data['businessObjectives']:
            st.markdown(f"- {obj}")
        
        st.markdown("#### Requirements")
        for req in brd_data['requirements']:
            priority_emoji = {'High': '🔴', 'Medium': '🟠', 'Low': '🟢'}.get(req['priority'], '⚪')
            st.markdown(f"{priority_emoji} **{req['id']}**: {req['description']} (*{req['priority']}*)")

def main():
    """Main application function."""
    # Render sidebar
    render_sidebar()
    
    # Main header
    st.markdown('<h1 class="main-header">🎯 ReqMind AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Project Alignment Intelligence Dashboard</p>', unsafe_allow_html=True)
    
    # Input Section
    st.markdown("## 📝 Input Communication")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        project_name = st.text_input(
            "Project Name",
            value="My Project",
            placeholder="Enter your project name"
        )
    
    with col2:
        if st.button("📋 Load Sample", use_container_width=True):
            st.session_state['sample_loaded'] = True
    
    # Text area for communication
    default_text = SAMPLE_SCENARIO if st.session_state.get('sample_loaded', False) else ""
    communication_text = st.text_area(
        "Paste stakeholder communication (Slack/Email/Meeting)",
        value=default_text,
        height=200,
        placeholder="Example:\nPM (Slack): We need delivery by March 30...\nClient (Email): I need delivery by April 10...\nDeveloper (Meeting): Backend dependency may delay..."
    )
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🚀 Analyze Alignment", use_container_width=True, type="primary")
    
    # Process analysis
    if analyze_button:
        if not communication_text.strip():
            st.error("⚠️ Please enter some communication text to analyze.")
            return
        
        if not project_name.strip():
            st.error("⚠️ Please enter a project name.")
            return
        
        # Show loading spinner
        with st.spinner("🔄 Analyzing alignment... This may take a few seconds."):
            try:
                # Call API
                result = call_alignment_api(project_name, communication_text)
                
                # Store in session state
                st.session_state['analysis_result'] = result
                st.session_state['analysis_timestamp'] = datetime.now()
                
                st.success("✅ Analysis complete!")
                
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend API. Please ensure the server is running at http://127.0.0.1:8000")
                return
            except requests.exceptions.Timeout:
                st.error("❌ Request timeout. The analysis is taking too long.")
                return
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                return
    
    # Display results if available
    if 'analysis_result' in st.session_state:
        result = st.session_state['analysis_result']
        
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        # Timestamp
        if 'analysis_timestamp' in st.session_state:
            st.caption(f"Analysis completed at: {st.session_state['analysis_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        alignment_data = result['alignment_analysis']
        brd_data = result['brd']
        
        # Top metrics row
        render_metrics_row(alignment_data)
        
        st.markdown("---")
        
        # Alert section
        render_alert_section(alignment_data['alert'], alignment_data['risk_level'])
        
        st.markdown("---")
        
        # Two column layout for detailed sections
        col1, col2 = st.columns(2)
        
        with col1:
            render_conflicts_section(alignment_data['conflicts'])
            st.markdown("---")
            render_volatility_section(alignment_data['requirement_volatility'])
        
        with col2:
            render_timeline_section(alignment_data['timeline_mismatches'])
            st.markdown("---")
            render_stakeholders_section(brd_data)
        
        st.markdown("---")
        
        # BRD Section
        render_brd_section(brd_data)
        
        # Download button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download Complete Analysis (JSON)",
                data=json_str,
                file_name=f"reqmind_analysis_{project_name.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
