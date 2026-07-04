import streamlit as st
import json
from scoring_engine import orchestrate_credit_assessment
from ai_engine import query_qwen_underwriter

st.set_page_config(page_title="IDBI MSME Credit Core", layout="wide")

st.title("🛡️ CredCard AI: Financial Health Card Platform")
st.subheader("Track 3 — Alternative Ingestion Engine for NTB/NTC Enterprise Underwriting")
st.markdown("---")

# ==========================================
# SIDEBAR: PIPELINE SOURCE SELECTION
# ==========================================
st.sidebar.header("🔌 Ingestion Mode Selector")
mode = st.sidebar.radio(
    "Choose Data Entry Method:",
    ["📄 Load Prime Profile (JSON)", "📄 Load Volatile Profile (JSON)", "📄 Load Stressed Profile (JSON)", "🛠️ Manual Judge Entry Mode"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Telemetry Metrics Ingestion")

# Establish variables dynamically based on selection
if "Manual" not in mode:
    # Map the radio choice to the correct mock JSON file
    file_map = {
        "📄 Load Prime Profile (JSON)": "mock_msme_prime.json",
        "📄 Load Volatile Profile (JSON)": "mock_msme_volatile.json",
        "📄 Load Stressed Profile (JSON)": "mock_msme_stressed.json"
    }
    target_file = file_map[mode]
    
    try:
        # Pull baseline calculations from the engine
        base_report = orchestrate_credit_assessment(target_file)
        with open(target_file, 'r') as f:
            raw_payload = json.load(f)
            
        raw_m = base_report["raw_metrics_summary"]
        
        # Display the ingested values as read-only values for the judges' reference
        input_company = st.sidebar.text_input("Entity Legal Name", value=base_report["company_name"], disabled=True)
        input_gst_delay = st.sidebar.number_input("Average GST Filing Delays (Days)", value=int(raw_m["gst_delay"]), disabled=True)
        input_upi_volatility = st.sidebar.number_input("Daily UPI Inflow Variance %", value=int(raw_m["upi_var"]), disabled=True)
        input_workforce_delta = st.sidebar.number_input("Net Employee Count Scaling Trend", value=int(raw_m["staff_delta"]), disabled=True)
        input_power_slope = st.sidebar.number_input("Factory Power Slope (kWh Delta)", value=int(raw_m["power_delta"]), disabled=True)
        
    except Exception as e:
        st.sidebar.error("Please run your data generator script to create the mock files first.")
        st.stop()
else:
    # Unlock full interactive manual entry for judges
    input_company = st.sidebar.text_input("Entity Legal Name", "Custom Enterprise Test Unit")
    input_gst_delay = st.sidebar.number_input("Average GST Filing Delays (Days)", min_value=0, max_value=90, value=12)
    input_upi_volatility = st.sidebar.number_input("Daily UPI Inflow Variance %", min_value=0, max_value=100, value=35)
    input_workforce_delta = st.sidebar.number_input("Net Employee Count Scaling Trend", min_value=-50, max_value=50, value=-2)
    input_power_slope = st.sidebar.number_input("Factory Power Slope (kWh Delta)", min_value=-5000, max_value=5000, value=-600)

# ==========================================
# PROCESSING & SCORING MATHEMATICS
# ==========================================
gst_score = max(0, 100 - (input_gst_delay * 3.5))
upi_score = max(0, 100 - (input_upi_volatility * 1.1))
epfo_score = min(100, max(0, 80 + (input_workforce_delta * 10)))
power_score = min(100, max(0, 75 + (input_power_slope * 0.02)))

composite_percentage = (gst_score * 0.30) + (upi_score * 0.30) + (epfo_score * 0.15) + (power_score * 0.25)
final_credit_score = int(300 + (composite_percentage * 6))

if final_credit_score >= 750:
    verdict = "DISCIPLINED (YES GO)"
    brief_description = "The enterprise displays robust cross-network operational health. Inward revenue vectors align smoothly against overhead profiles."
elif final_credit_score >= 550:
    verdict = "NON-DISCIPLINED (MANUAL REVIEW)"
    brief_description = "The applicant exhibits decent revenue baselines but displays localized systemic friction or operational volatility."
else:
    verdict = "STRESSED (NO GO)"
    brief_description = "High operational and transactional risk detected. Critical ambient indicators point to a severe contraction or possible idling of operations."

compiled_report = {
    "company_name": input_company,
    "financial_health_score": f"{final_credit_score} / 900",
    "health_percentage": f"{round(composite_percentage, 1)}%",
    "underwriting_verdict": verdict,
    "raw_metrics_summary": {
        "avg_gst_filing_delay_days": input_gst_delay,
        "daily_upi_variance_percentage": input_upi_volatility,
        "net_workforce_growth_count": input_workforce_delta,
        "electricity_consumption_kwh_slope": input_power_slope
    }
}

# ==========================================
# MAIN DASHBOARD UI DISPLAY RENDER
# ==========================================
if "YES GO" in verdict: st.success(f"### 🟩 UNDERWRITING MATRIX DECISION: {verdict}")
elif "MANUAL REVIEW" in verdict: st.warning(f"### 🟨 UNDERWRITING MATRIX DECISION: {verdict}")
else: st.error(f"### 🟥 UNDERWRITING MATRIX DECISION: {verdict}")

col1, col2, col3 = st.columns(3)
with col1: st.metric(label="Registered Trading Entity", value=input_company)
with col2: st.metric(label="Alternative Credit Health Index", value=f"{final_credit_score} / 900")
with col3: st.metric(label="Ecosystem Integrity Density", value=f"{round(composite_percentage, 1)}%")

st.markdown("---")
st.markdown("#### 📝 Executive Rule-Engine Summary Brief")
st.info(brief_description)

# Clean, contextual display of the active JSON raw text if a JSON profile is selected
if "Manual" not in mode:
    st.markdown("---")
    if st.checkbox("🔍 View Secure Data Stream JSON Ingestion Logs"):
        st.json(raw_payload)

st.markdown("---")

# ==========================================
# STANDALONE COGNITIVE CHATBOT ENGINE SECTION
# ==========================================
st.markdown("#### 🤖 Proprietary Qwen Credit Assistant")
st.caption("Ask questions or request strategic forecasts using your running qwen3:8b model library:")

user_query = st.text_input("Query Central Bank Agent Engine:", placeholder="e.g., Run a full 180-day forecast memo based on these values...")
if user_query:
    st.markdown(f"💬 **Relationship Manager Inquiry:** {user_query}")
    with st.spinner("Local Qwen Core processing instruction training matrix..."):
        ai_response = query_qwen_underwriter(compiled_report, user_query)
    st.markdown(f"🤖 **Qwen Underwriter Core:**")
    st.write(ai_response)