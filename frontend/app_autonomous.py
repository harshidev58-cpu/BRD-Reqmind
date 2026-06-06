"""
ReqMind AI - Autonomous Multi-Channel Intelligence Dashboard
Showcases autonomous data ingestion from Gmail, Slack, Enron emails, and AMI transcripts
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ReqMind AI - Autonomous Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --dark-bg: #1a1a2e;
        --accent: #667eea;
        --glass: rgba(255, 255, 255, 0.05);
    }
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #a0a0a0;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: var(--glass);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: center;
    }
    .data-source-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #00cc66;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border-left: 4px solid #0c5460;
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
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"
DATASET_ENDPOINT = f"{API_BASE_URL}/dataset/generate_brd_from_dataset"
STATUS_ENDPOINT = f"{API_BASE_URL}/dataset/dataset_status"

def check_dataset_status():
    """Check dataset configuration status."""
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

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
    """Render the sidebar."""
    with st.sidebar:
        st.markdown("### 🤖 ReqMind AI")
        st.markdown("**Autonomous Intelligence**")
        st.markdown("---")
        
        # Dataset Status
        st.markdown("### 📊 Dataset Status")
        status = check_dataset_status()
        
        if status:
            if status['dataset_mode_enabled']:
                st.markdown('<div class="success-box">✅ Dataset Mode Active</div>', unsafe_allow_html=True)
                
                st.markdown("**Configuration:**")
                st.markdown(f"- Emails: {'✅' if status['email_dataset_configured'] else '❌'}")
                st.markdown(f"- Meetings: {'✅' if status['meeting_dataset_configured'] else '❌'}")
                st.markdown(f"- Max Emails: {status['max_emails']}")
                st.markdown(f"- Max Meetings: {status['max_meetings']}")
            else:
                st.warning("⚠️ Dataset mode disabled")
        else:
            st.error("❌ Backend Disconnected")
        
        st.markdown("---")
        
        # Data Sources
        st.markdown("### 📡 Data Sources")
        st.markdown("""
        **Autonomous Ingestion:**
        - 📧 Enron Email Dataset
        - 💬 Slack Simulation
        - 🎤 AMI Meeting Transcripts
        - 🔍 Keyword Filtering
        - 🤖 Auto-conflict Detection
        """)
        
        st.markdown("---")
        st.caption(f"© 2024 ReqMind AI | v2.0")

def main():
    """Main application function."""
    render_sidebar()
    
    # Main header
    st.markdown('<h1 class="main-header">🤖 ReqMind AI - Autonomous Mode</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Autonomous Multi-Channel Intelligence from Real-World Datasets</p>', unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("## ✨ Autonomous Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📧 Email Intelligence</h3>
            <p>Automatically ingests and analyzes Enron email dataset with 500K+ real business emails</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>💬 Slack Simulation</h3>
            <p>Converts email threads to Slack-style messages for multi-channel analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🎤 Meeting Transcripts</h3>
            <p>Processes AMI meeting corpus with 279 real design meeting transcripts</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Dataset Information
    st.markdown("## 📊 Available Datasets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="data-source-card">
            <h4>📧 Enron Email Dataset</h4>
            <p><strong>Source:</strong> Public Domain</p>
            <p><strong>Size:</strong> ~500,000 emails from 150 employees</p>
            <p><strong>Content:</strong> Real business communication including:</p>
            <ul>
                <li>Project discussions and decisions</li>
                <li>Timeline negotiations</li>
                <li>Requirement changes</li>
                <li>Stakeholder disagreements</li>
            </ul>
            <p><strong>Status:</strong> ✅ Loaded and Ready</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="data-source-card">
            <h4>🎤 AMI Meeting Corpus</h4>
            <p><strong>Source:</strong> CC BY 4.0</p>
            <p><strong>Size:</strong> 279 meeting transcripts</p>
            <p><strong>Content:</strong> Scenario-based design meetings with:</p>
            <ul>
                <li>Requirements discussions</li>
                <li>Design decisions</li>
                <li>Feature prioritization</li>
                <li>Timeline planning</li>
            </ul>
            <p><strong>Status:</strong> ✅ Loaded and Ready</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Input Section
    st.markdown("## 🎯 Generate BRD from Datasets")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        project_name = st.text_input(
            "Project Name",
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
            help="Number of items to sample from datasets"
        )
    
    # Keywords input
    keywords_input = st.text_input(
        "Keywords (comma-separated)",
        value="project, deadline, requirement, feature, design",
        placeholder="e.g., project, deadline, requirement, timeline",
        help="Filter dataset content by these keywords"
    )
    
    keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    
    # Preset scenarios
    st.markdown("### 🎬 Preset Scenarios")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📅 Timeline Conflicts", use_container_width=True):
            st.session_state['preset'] = {
                'name': 'Timeline Conflict Analysis',
                'keywords': ['deadline', 'timeline', 'delivery', 'schedule', 'date']
            }
    
    with col2:
        if st.button("📋 Requirement Changes", use_container_width=True):
            st.session_state['preset'] = {
                'name': 'Requirement Volatility Analysis',
                'keywords': ['requirement', 'feature', 'specification', 'scope', 'change']
            }
    
    with col3:
        if st.button("⚔️ Stakeholder Conflicts", use_container_width=True):
            st.session_state['preset'] = {
                'name': 'Stakeholder Disagreement Analysis',
                'keywords': ['disagree', 'concern', 'issue', 'problem', 'conflict']
            }
    
    # Apply preset if selected
    if 'preset' in st.session_state:
        preset = st.session_state['preset']
        project_name = preset['name']
        keywords = preset['keywords']
        st.info(f"📌 Preset loaded: {preset['name']}")
        st.info(f"🔍 Keywords: {', '.join(keywords)}")
    
    st.markdown("---")
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🚀 Analyze from Datasets", use_container_width=True, type="primary")
    
    # Process analysis
    if analyze_button:
        if not project_name.strip():
            st.error("⚠️ Please enter a project name.")
            return
        
        # Show loading with progress
        with st.spinner("🤖 Autonomous analysis in progress..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("📧 Loading Enron emails...")
                progress_bar.progress(20)
                
                status_text.text("🎤 Loading AMI meeting transcripts...")
                progress_bar.progress(40)
                
                status_text.text("💬 Simulating Slack messages...")
                progress_bar.progress(60)
                
                status_text.text("🔍 Analyzing alignment...")
                progress_bar.progress(80)
                
                # Call API
                result = call_dataset_api(project_name, keywords, sample_size)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Store in session state
                st.session_state['dataset_result'] = result
                st.session_state['analysis_timestamp'] = datetime.now()
                
                st.success("✅ Autonomous analysis complete!")
                
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend API.")
                return
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    st.error("❌ No relevant content found with the provided keywords. Try different keywords.")
                elif e.response.status_code == 400:
                    st.error("❌ Dataset mode is not enabled. Please configure dataset paths in .env")
                else:
                    st.error(f"❌ Error: {e.response.text}")
                return
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                return
    
    # Display results
    if 'dataset_result' in st.session_state:
        result = st.session_state['dataset_result']
        
        st.markdown("---")
        st.markdown("## 📊 Autonomous Analysis Results")
        
        # Timestamp
        if 'analysis_timestamp' in st.session_state:
            st.caption(f"Analysis completed at: {st.session_state['analysis_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Metadata
        metadata = result.get('metadata', {})
        if metadata:
            st.markdown("### 📈 Data Processing Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📧 Emails Processed", metadata.get('email_count', 0))
            with col2:
                st.metric("🎤 Meetings Processed", metadata.get('meeting_count', 0))
            with col3:
                st.metric("🔍 Keywords Used", len(metadata.get('keywords_used', [])))
            
            if metadata.get('keywords_used'):
                st.caption(f"Keywords: {', '.join(metadata['keywords_used'])}")
        
        st.markdown("---")
        
        # Conflicts detected
        conflicts = result.get('conflicts', [])
        if conflicts:
            st.markdown("### ⚔️ Auto-Detected Conflicts")
            st.warning(f"🚨 {len(conflicts)} conflicts detected across data sources")
            
            for i, conflict in enumerate(conflicts, 1):
                with st.expander(f"Conflict {i}: {conflict.get('type', 'Unknown').replace('_', ' ').title()}", expanded=True):
                    st.markdown(f"**Pattern 1:** {conflict.get('pattern1', 'N/A')}")
                    st.markdown(f"**Pattern 2:** {conflict.get('pattern2', 'N/A')}")
                    st.markdown(f"**Sources with Pattern 1:** {', '.join(conflict.get('sources_pattern1', []))}")
                    st.markdown(f"**Sources with Pattern 2:** {', '.join(conflict.get('sources_pattern2', []))}")
                    st.markdown(f"**Severity:** {conflict.get('severity', 'unknown').upper()}")
        else:
            st.success("✅ No conflicts detected in the analyzed data")
        
        st.markdown("---")
        
        # BRD Section
        brd_data = result
        st.markdown("### 📄 Generated BRD")
        
        with st.expander("View Complete BRD", expanded=True):
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
            
            st.markdown("#### Stakeholders")
            for stakeholder in brd_data.get('stakeholders', []):
                st.markdown(f"- **{stakeholder['name']}** - {stakeholder['role']}")
        
        # Download button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download Complete Analysis (JSON)",
                data=json_str,
                file_name=f"autonomous_analysis_{project_name.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
