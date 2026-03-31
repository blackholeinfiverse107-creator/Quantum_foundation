import streamlit as st
from intelligence_core.core import IntelligenceCore
from sankalp.adapter import IntelligenceAdapter
from sankalp.engine import ResponseComposerEngine

st.set_page_config(page_title="AI Being", layout="centered")
st.title("AI Being – Streamlit Demo")

message = st.text_input("Message", "Hello, how are you?")
user_age = st.number_input("User Age", min_value=0, max_value=120, value=25)
region = st.selectbox("Region", ["US", "EU", "unknown"], index=0)
karma_score = st.number_input("Karma Score", min_value=0, max_value=100, value=80)
risk_signal = st.selectbox("Risk Signal", ["low", "medium", "high"], index=0)

run = st.button("Run")

if run:
    brain = IntelligenceCore()
    context = {"user_age": int(user_age), "region": region}
    karma = {"karma_score": int(karma_score), "risk_signal": risk_signal}
    bucket = {"baseline_emotional_band": "neutral", "previous_state_anchor": "neutral"}
    embodiment_output, _ = brain.process_interaction(context, karma, bucket, message_content=message)
    sankalp_input = IntelligenceAdapter.adapt(
        embodiment_output=embodiment_output,
        original_context=context,
        original_karma=karma,
        message_content=message,
        context_summary="Streamlit interaction"
    )
    engine = ResponseComposerEngine()
    response_block = engine.process(sankalp_input)
    resp = response_block.to_dict()
    st.subheader("Response")
    st.write(resp.get("message_primary", ""))
    col1, col2, col3 = st.columns(3)
    col1.metric("Tone", resp.get("tone_profile", ""))
    col2.metric("Voice", resp.get("voice_profile", ""))
    col3.metric("Expression", resp.get("emotional_depth", ""))
    st.write("Safety Flags:", ", ".join(resp.get("content_safety_flags", [])))
    st.write("Boundaries:", ", ".join(resp.get("boundaries_enforced", [])))
    st.write("Pacing:", resp.get("pacing_hint", ""))
    st.write("Delivery:", resp.get("delivery_style", ""))
    st.json(resp)

