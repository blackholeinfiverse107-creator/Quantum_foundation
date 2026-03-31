import sys
import os
import streamlit as st

# Add project root to path to find modules
current_dir = os.path.dirname(os.path.abspath(__file__))
spine_root = os.path.join(current_dir, "Backend Stability Spine")
# Insert at 0 to ensure we load from Backend Stability Spine, not local 'sankalp' folder
sys.path.insert(0, spine_root)

# Import the production engine
from app.core.sankalp.engine import SankalpEngine

st.set_page_config(page_title="Sankalp Response Engine", layout="centered")
st.title("Sankalp Response Intelligence Demo")

st.markdown("### Integration Phase C: Response Convergence")

# Sidebar for Context
st.sidebar.header("Context Simulation")
platform = st.sidebar.selectbox("Platform", ["web", "mobile", "voice"])
karma = st.sidebar.slider("Karma Score", 0, 100, 80)
risk_flags = st.sidebar.multiselect("Risk Flags", ["self_harm", "profanity", "aggression"])
priority = st.sidebar.selectbox("Priority", ["normal", "high"])

# Main Input
query = st.text_input("User Input", "What's the weather like?")
run = st.button("Generate Response")

if run:
    # Initialize Engine
    engine = SankalpEngine()
    
    # Mock LLM Response (since we don't have the full Intelligence Core here)
    mock_llm_response = f"The weather is sunny and 25 degrees. (Processed input: {query})"
    
    # Build Context
    context = {
        "platform": platform,
        "karma_score": karma,
        "risk_flags": risk_flags,
        "priority": priority
    }
    
    # Process
    result = engine.process_response(query, mock_llm_response, context)
    
    # Display Result
    st.subheader("Assistant Response")
    st.info(result.get("message_primary", "No response generated."))
    
    # Display Meta / Logic
    st.subheader("Decision Logic")
    col1, col2, col3 = st.columns(3)
    
    meta = result.get("meta", {})
    col1.metric("Response Type", meta.get("response_type", "N/A"))
    col2.metric("Urgency", meta.get("urgency_level", "N/A"))
    col3.metric("Voice Profile", result.get("voice_profile", "N/A"))
    
    st.write("**Tone Profile:**", result.get("tone_profile", "N/A"))
    st.write("**Trace ID:**", result.get("trace_id"))
    st.write("**Boundaries Enforced:**", result.get("boundaries_enforced", []))
    
    st.expander("Full Debug Output").json(result)

