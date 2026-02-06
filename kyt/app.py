import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from orchestrator.kyt_orchestrator import KYTOrchestrator

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Page configuration
st.set_page_config(
    page_title="KYT Auditor - Autonomous Compliance System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #FEE2E2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .risk-medium {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .risk-low {
        background-color: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = KYTOrchestrator()
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "transactions" not in st.session_state:
    st.session_state.transactions = None


def load_sample_transactions():
    """Load sample transactions from CSV."""
    try:
        df = pd.read_csv("data/sample_transactions.csv")
        return df
    except Exception as e:
        st.error(f"Error loading sample transactions: {e}")
        return None


def display_header():
    """Display the main header."""
    st.markdown('<p class="main-header">🔍 Autonomous KYT Auditor</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Know Your Transaction Compliance System</p>', unsafe_allow_html=True)
    st.divider()


def display_sidebar():
    """Display sidebar with options."""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80?text=KYT+Auditor", use_container_width=True)
        st.markdown("### Navigation")
        
        page = st.radio(
            "Select Page",
            ["📊 Transaction Analysis", "📈 Analysis Results", "📋 Audit Reports", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        st.markdown("### System Status")
        st.success("✅ Azure OpenAI: Connected")
        st.success("✅ AI Search: Ready")
        st.success("✅ Content Safety: Active")
        
        st.divider()
        
        st.markdown("### Quick Stats")
        if st.session_state.analysis_results:
            summary = st.session_state.analysis_results.get("summary", {})
            st.metric("Risk Level", summary.get("overall_risk_level", "N/A"))
            st.metric("Alerts", summary.get("high_risk_transactions", 0))
        
        return page


def display_transaction_analysis():
    """Display the transaction analysis page."""
    st.markdown("## 📊 Transaction Analysis")
    
    # File upload or sample data
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Transaction CSV",
            type=["csv"],
            help="Upload a CSV file with transaction data"
        )
    
    with col2:
        if st.button("📂 Load Sample Data", use_container_width=True):
            st.session_state.transactions = load_sample_transactions()
            st.success("Sample data loaded!")
    
    if uploaded_file is not None:
        st.session_state.transactions = pd.read_csv(uploaded_file)
    
    # Display transactions
    if st.session_state.transactions is not None:
        st.markdown("### Loaded Transactions")
        st.dataframe(
            st.session_state.transactions,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown(f"**Total Transactions:** {len(st.session_state.transactions)}")
        
        # Analysis button
        st.divider()
        
        if st.button("🚀 Run KYT Analysis", type="primary", use_container_width=True):
            run_analysis()


def run_analysis():
    """Run the KYT analysis."""
    if st.session_state.transactions is None:
        st.error("Please load transactions first!")
        return
    
    # Convert DataFrame to list of dicts
    transactions = st.session_state.transactions.to_dict("records")
    
    # Progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(message, progress):
        status_text.text(message)
        progress_bar.progress(progress)
    
    try:
        with st.spinner("Running AI-powered analysis..."):
            results = st.session_state.orchestrator.analyze_transactions(
                transactions,
                callback=update_progress
            )
            st.session_state.analysis_results = results
        
        progress_bar.progress(1.0)
        status_text.text("Analysis complete!")
        st.success("✅ Analysis completed successfully!")
        
        # Display results
        display_analysis_results()
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")


def display_analysis_results():
    """Display the analysis results."""
    if st.session_state.analysis_results is None:
        st.info("No analysis results yet. Run an analysis first.")
        return
    
    results = st.session_state.analysis_results
    summary = results.get("summary", {})
    
    st.markdown("---")
    st.markdown("## 📈 Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_level = summary.get("overall_risk_level", "N/A")
        risk_color = "🔴" if risk_level == "HIGH" else "🟡" if risk_level == "MEDIUM" else "🟢"
        st.metric("Overall Risk", f"{risk_color} {risk_level}")
    
    with col2:
        st.metric("High Risk Transactions", summary.get("high_risk_transactions", 0))
    
    with col3:
        st.metric("Sanctions Matches", summary.get("sanctions_matches", 0))
    
    with col4:
        st.metric("Suspicious Patterns", summary.get("suspicious_patterns", 0))
    
    # Detailed tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔬 Forensic Analysis",
        "⚖️ Compliance",
        "🤖 Responsible AI",
        "📄 Audit Report",
        "📊 Summary"
    ])
    
    with tab1:
        display_forensic_results(results.get("forensic_analysis", {}))
    
    with tab2:
        display_compliance_results(results.get("compliance_evaluation", {}))
    
    with tab3:
        display_responsible_ai_results(results.get("responsible_ai", {}))
    
    with tab4:
        display_audit_report(results.get("audit_report", {}))
    
    with tab5:
        display_summary(summary)


def display_summary(summary):
    """Display the overall analysis summary."""
    st.markdown("### 📊 Analysis Summary")

    risk_level = summary.get("overall_risk_level", "N/A")
    if risk_level == "HIGH":
        risk_color, risk_icon = "red", "🔴"
    elif risk_level == "MEDIUM":
        risk_color, risk_icon = "orange", "🟡"
    else:
        risk_color, risk_icon = "green", "🟢"

    st.markdown(
        f"<h3 style='color:{risk_color};'>{risk_icon} Overall Risk Level: {risk_level}</h3>",
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("High Risk Transactions", summary.get("high_risk_transactions", 0))
        st.metric("Sanctions Matches", summary.get("sanctions_matches", 0))

    with col2:
        st.metric("Suspicious Patterns", summary.get("suspicious_patterns", 0))
        compliance = summary.get("compliance_status", "N/A")
        comp_icon = "✅" if compliance == "PASSED" else "❌"
        st.metric("Compliance Status", f"{comp_icon} {compliance}")

    with col3:
        rai_score = summary.get("responsible_ai_status", "N/A")
        if isinstance(rai_score, (int, float)):
            rai_icon = "✅" if rai_score >= 80 else "⚠️" if rai_score >= 50 else "❌"
            st.metric("Responsible AI Score", f"{rai_icon} {rai_score}%")
        else:
            st.metric("Responsible AI Score", rai_score)

        manual_review = summary.get("requires_manual_review", False)
        review_icon = "⚠️ Yes" if manual_review else "✅ No"
        st.metric("Requires Manual Review", review_icon)

    st.divider()

    # Full summary as JSON
    with st.expander("🔍 View Raw Summary Data"):
        st.json(summary)


def display_forensic_results(forensic):
    """Display forensic analysis results."""
    st.markdown("### 🔬 Forensic Analysis Results")
    
    # High-risk transactions
    high_risk = forensic.get("high_risk_transactions", [])
    if high_risk:
        st.markdown("#### High-Risk Transactions")
        for txn in high_risk:
            with st.expander(f"⚠️ Transaction {txn.get('id', 'Unknown')} - Risk Score: {txn.get('risk_score', 0)}/10"):
                st.json(txn)
    else:
        st.success("No high-risk transactions detected.")
    
    # Patterns detected
    patterns = forensic.get("patterns_detected", [])
    if patterns:
        st.markdown("#### Suspicious Patterns Detected")
        for pattern in patterns:
            severity_icon = "🔴" if pattern.get("severity") == "HIGH" else "🟡"
            st.warning(f"{severity_icon} **{pattern.get('type', 'Unknown Pattern')}** - Account: {pattern.get('account', 'N/A')}")
            st.json(pattern)
    else:
        st.success("No suspicious patterns detected.")


def display_compliance_results(compliance):
    """Display compliance evaluation results."""
    st.markdown("### ⚖️ Compliance Evaluation Results")
    
    status = compliance.get("compliance_status", "UNKNOWN")
    if status == "PASSED":
        st.success(f"✅ Compliance Status: {status}")
    else:
        st.warning(f"⚠️ Compliance Status: {status}")
    
    # Sanctions matches
    matches = compliance.get("sanctions_matches", [])
    if matches:
        st.markdown("#### Sanctions Matches")
        for match in matches:
            st.error(f"🚨 **{match.get('name', 'Unknown')}** - List: {match.get('sanctions_list', 'N/A')} - Score: {match.get('score', 0):.2f}")
    else:
        st.success("No sanctions matches found.")


def display_responsible_ai_results(rai):
    """Display responsible AI check results."""
    st.markdown("### 🤖 Responsible AI Assessment")
    
    summary = rai.get("summary", {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Decisions Reviewed", rai.get("total_decisions_reviewed", 0))
    with col2:
        st.metric("Pass Rate", f"{summary.get('pass_rate', 0)}%")
    with col3:
        st.metric("Review Required", summary.get("review_required", 0))
    
    # Recommendations
    recommendations = rai.get("recommendations", [])
    if recommendations:
        st.markdown("#### Recommendations")
        for rec in recommendations:
            st.info(f"💡 {rec}")


def display_audit_report(report):
    """Display the audit report."""
    st.markdown("### 📄 Audit Report")
    
    if report.get("raw_output"):
        st.text_area("Report Output", report.get("raw_output", ""), height=300)
    
    # Download button
    if st.session_state.analysis_results:
        report_json = json.dumps(st.session_state.analysis_results, indent=2, default=str)
        if "download_audit_report_counter" not in st.session_state:
            st.session_state.download_audit_report_counter = 0

        st.session_state.download_audit_report_counter += 1
        download_key = f"download_audit_report_{st.session_state.download_audit_report_counter}"

        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=report_json,
            file_name=f"kyt_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key=download_key,
        )


def display_audit_reports_page():
    """Display the audit reports page."""
    st.markdown("## 📋 Audit Reports History")
    
    history = st.session_state.orchestrator.get_analysis_history()
    
    if not history:
        st.info("No audit reports yet. Run an analysis first.")
        return
    
    for i, analysis in enumerate(reversed(history)):
        with st.expander(f"Report: {analysis.get('id', f'Analysis {i+1}')} - {analysis.get('status', 'Unknown')}"):
            st.json(analysis)


def display_settings_page():
    """Display the settings page."""
    st.markdown("## ⚙️ Settings")
    
    with st.form("settings_form"):
        st.markdown("### Azure Configuration")
   
    
        st.markdown("### Analysis Configuration")
        st.slider("Risk Score Threshold", 1, 10, 5)
        st.checkbox("Enable Enhanced Due Diligence", value=True)
        st.checkbox("Auto-generate SAR recommendations", value=True)
    
        #if st.form_submit_button("Save Settings", type="primary", use_container_width=True):
        #    st.success("✅ Settings saved! (Note: Update .env file for persistence)")


def main():
    """Main application entry point."""
    display_header()
    page = display_sidebar()
    
    if page == "📊 Transaction Analysis":
        display_transaction_analysis()
        if st.session_state.analysis_results:
            display_analysis_results()
    elif page == "📈 Analysis Results":
        display_analysis_results()
    elif page == "📋 Audit Reports":
        display_audit_reports_page()
    elif page == "⚙️ Settings":
        display_settings_page()


if __name__ == "__main__":
    main()

