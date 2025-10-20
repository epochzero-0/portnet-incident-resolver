"""
PORTNET Incident Resolver - Streamlit Web Application
Main entry point for the web interface
"""
import sys
from pathlib import Path
import streamlit as st
from datetime import datetime

# Add src directory to Python path
SRC_DIR = Path(__file__).parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analyzers import IncidentParser, ContextGatherer, AIAnalyzer
from utils.config import validate_files, validate_azure_config

# Page configuration
st.set_page_config(
    page_title="PORTNET Incident Resolver",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4788;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f4788;
        color: white;
        font-weight: 600;
        padding: 0.75rem;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #163661;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'parsed_incident' not in st.session_state:
        st.session_state.parsed_incident = None
    if 'context' not in st.session_state:
        st.session_state.context = None
    if 'analysis' not in st.session_state:
        st.session_state.analysis = None
    if 'remediation' not in st.session_state:
        st.session_state.remediation = None
    if 'escalation_l3' not in st.session_state:
        st.session_state.escalation_l3 = None
    if 'escalation_mgmt' not in st.session_state:
        st.session_state.escalation_mgmt = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False


def validate_system():
    """Validate system configuration"""
    try:
        validate_files()
        validate_azure_config()
        return True, "✅ System validated successfully"
    except Exception as e:
        return False, f"❌ Validation failed: {str(e)}"


def main():
    """Main application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🚢 PORTNET Incident Resolver</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Incident Analysis & Resolution</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 System Status")
        
        # Validate system
        is_valid, message = validate_system()
        if is_valid:
            st.success(message)
        else:
            st.error(message)
            st.stop()
        
        st.divider()
        
        st.header("ℹ️ About")
        st.markdown("""
        This system helps duty officers:
        - 🔍 Analyze incidents quickly
        - 📊 Find root causes
        - 🔧 Generate remediation plans
        - 📤 Create escalation summaries
        
        **Powered by Azure OpenAI**
        """)
        
        st.divider()
        
        # Sample test cases
        st.header("📝 Sample Test Cases")
        if st.button("Load Test Case 1: Duplicate Container"):
            st.session_state.sample_incident = """RE: Email ALR-861600 | CMAU0000020 - Duplicate Container information received

To: Ops Team Duty; Jen
Cc: Customer Service

Hi Jen,

Please assist in checking container CMAU0000020. Customer on PORTNET is seeing 2 identical containers information.

Thanks.
Regards,
Kenny"""
        
        if st.button("Load Test Case 2: Vessel Error"):
            st.session_state.sample_incident = """RE: Email ALR-861631 | VESSEL_ERR_4 - System Vessel Name has been used by other vessel advice

To: Ops Team Duty; Vedu
Cc: Customer Service

Hi Vedu,

Customer reported that they were unable to create vessel advice for MV Lion City 07 and hit error VESSEL_ERR_4. The local vessel name had been used by other vessel advice.

Please assist, thanks.
Regards,
Jia Xuan"""
        
        if st.button("Load Test Case 3: EDI Stuck"):
            st.session_state.sample_incident = """Alert: SMS INC-154599

Issue: EDI message REF-IFT-0007 stuck in ERROR status (Sender: LINE-PSA, Recipient: PSA-TOS, State: No acknowledgment sent, ack_at is NULL)."""
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📥 Incident Input", "📊 Analysis Results", "📤 Escalation Summaries"])
    
    # Tab 1: Incident Input
    with tab1:
        st.header("Incident Details")
        
        # Check if sample incident loaded
        default_text = st.session_state.get('sample_incident', '')
        
        incident_text = st.text_area(
            "Paste incident report (email, SMS, or call details):",
            value=default_text,
            height=300,
            placeholder="Paste the incident details here...\n\nExample:\nRE: Email ALR-861600 | CMAU0000020 - Duplicate Container\nCustomer seeing duplicate containers..."
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            analyze_button = st.button("🔍 Analyze Incident", type="primary", use_container_width=True)
        
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.session_state.clear()
            st.session_state.sample_incident = ''
            st.rerun()
        
        if analyze_button:
            if not incident_text.strip():
                st.error("⚠️ Please enter incident details")
            else:
                with st.spinner("🔄 Analyzing incident..."):
                    try:
                        # Step 1: Parse incident
                        with st.status("Parsing incident...", expanded=True) as status:
                            parser = IncidentParser()
                            parsed = parser.parse(incident_text)
                            st.session_state.parsed_incident = parsed
                            st.write("✅ Incident parsed successfully")
                            st.write(f"Type: {parsed['incident_type']}")
                            st.write(f"Module: {parsed['module']}")
                            st.write(f"Severity: {parsed['severity']}")
                            
                            # Step 2: Gather context
                            status.update(label="Gathering context from all sources...")
                            gatherer = ContextGatherer()
                            context = gatherer.gather(parsed)
                            st.session_state.context = context
                            st.write("✅ Context gathered")
                            
                            # Step 3: AI Analysis
                            status.update(label="Analyzing with AI...")
                            analyzer = AIAnalyzer()
                            analysis = analyzer.analyze_incident(parsed, context)
                            st.session_state.analysis = analysis
                            st.write("✅ AI analysis complete")
                            
                            # Step 4: Remediation Plan
                            status.update(label="Generating remediation plan...")
                            remediation = analyzer.generate_remediation_plan(parsed, context, analysis)
                            st.session_state.remediation = remediation
                            st.write("✅ Remediation plan generated")
                            
                            # Step 5: Escalation Summaries
                            status.update(label="Creating escalation summaries...")
                            escalation_l3 = analyzer.generate_escalation_summary(parsed, analysis, remediation, 'L3')
                            escalation_mgmt = analyzer.generate_escalation_summary(parsed, analysis, remediation, 'management')
                            st.session_state.escalation_l3 = escalation_l3
                            st.session_state.escalation_mgmt = escalation_mgmt
                            st.write("✅ Escalation summaries created")
                            
                            status.update(label="✅ Analysis complete!", state="complete", expanded=False)
                        
                        st.session_state.analysis_complete = True
                        st.success("🎉 Analysis completed successfully! View results in the tabs above.")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
    
    # Tab 2: Analysis Results
    with tab2:
        if not st.session_state.analysis_complete:
            st.info("👈 Enter an incident in the 'Incident Input' tab and click 'Analyze' to see results here.")
        else:
            st.header("Analysis Results")
            
            parsed = st.session_state.parsed_incident
            context = st.session_state.context
            analysis = st.session_state.analysis
            remediation = st.session_state.remediation
            
            # Incident Summary
            with st.expander("📋 Incident Summary", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Type", parsed['incident_type'].replace('_', ' ').title())
                with col2:
                    st.metric("Module", parsed['module'])
                with col3:
                    severity_color = {
                        'LOW': '🟢',
                        'MEDIUM': '🟡',
                        'HIGH': '🟠',
                        'CRITICAL': '🔴'
                    }
                    st.metric("Severity", f"{severity_color.get(parsed['severity'], '⚪')} {parsed['severity']}")
                
                if parsed['entities']:
                    st.subheader("Entities Found:")
                    for entity_type, values in parsed['entities'].items():
                        st.write(f"**{entity_type.title()}:** {', '.join(values)}")
            
            # Root Cause Analysis
            with st.expander("🎯 Root Cause Analysis", expanded=True):
                st.markdown(f"**Root Cause:**")
                st.write(analysis.get('root_cause', 'N/A'))
                
                st.markdown(f"**Impact:**")
                st.write(analysis.get('impact', 'N/A'))
                
                st.markdown(f"**Confidence Level:**")
                confidence = analysis.get('confidence', 'N/A')
                if 'HIGH' in confidence.upper():
                    st.success(f"🟢 {confidence}")
                elif 'MEDIUM' in confidence.upper():
                    st.warning(f"🟡 {confidence}")
                else:
                    st.info(f"⚪ {confidence}")
            
            # Context Found
            with st.expander("📚 Context Found"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Application Logs")
                    st.write(context['logs']['summary'])
                    
                    st.subheader("Historical Cases")
                    st.write(context['historical_cases']['summary'])
                
                with col2:
                    st.subheader("Knowledge Base")
                    st.write(context['knowledge_base']['summary'])
                    
                    st.subheader("Escalation Contacts")
                    st.write(context['escalation_contacts']['summary'])
            
            # Remediation Plan
            with st.expander("🔧 Remediation Plan", expanded=True):
                st.subheader("Pre-checks")
                st.write(remediation.get('pre_checks', 'N/A'))
                
                st.subheader("Remediation Steps")
                st.write(remediation.get('steps', 'N/A'))
                
                st.subheader("Verification")
                st.write(remediation.get('verification', 'N/A'))
                
                # Download full plan
                if st.download_button(
                    "📥 Download Complete Remediation Plan",
                    data=remediation.get('full_response', ''),
                    file_name=f"remediation_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                ):
                    st.success("Downloaded!")
    
    # Tab 3: Escalation Summaries
    with tab3:
        if not st.session_state.analysis_complete:
            st.info("👈 Enter an incident in the 'Incident Input' tab and click 'Analyze' to see escalation summaries here.")
        else:
            st.header("Escalation Summaries")
            
            # L3 Technical Summary
            st.subheader("📧 L3 Engineering Escalation")
            st.markdown("**Ready to send to L3 Engineering team:**")
            
            escalation_l3 = st.session_state.escalation_l3
            st.text_area(
                "L3 Escalation Email",
                value=escalation_l3,
                height=400,
                key="l3_text"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.download_button(
                    "📥 Download L3 Summary",
                    data=escalation_l3,
                    file_name=f"escalation_l3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                ):
                    st.success("Downloaded!")
            
            with col2:
                if st.button("📋 Copy to Clipboard", key="copy_l3", use_container_width=True):
                    st.toast("✅ Copied to clipboard!")
            
            st.divider()
            
            # Management Summary
            st.subheader("📧 Management Escalation")
            st.markdown("**Ready to send to Management:**")
            
            escalation_mgmt = st.session_state.escalation_mgmt
            st.text_area(
                "Management Escalation Email",
                value=escalation_mgmt,
                height=300,
                key="mgmt_text"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.download_button(
                    "📥 Download Management Summary",
                    data=escalation_mgmt,
                    file_name=f"escalation_mgmt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                ):
                    st.success("Downloaded!")
            
            with col2:
                if st.button("📋 Copy to Clipboard", key="copy_mgmt", use_container_width=True):
                    st.toast("✅ Copied to clipboard!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>PORTNET Incident Resolver | Powered by Azure OpenAI</p>
        <p style='font-size: 0.9rem;'>Built for PSA Singapore Maritime Operations</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()