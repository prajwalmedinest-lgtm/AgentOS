import streamlit as st
import os
from dotenv import load_dotenv

# -----------------------------
# LOAD ENV (SECURE API KEY)
# -----------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Agent-OS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# CUSTOM CSS (PREMIUM UI)
# -----------------------------
st.markdown("""
<style>
/* GLOBAL */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0b0f1a 0%, #111827 100%);
    color: #e5e7eb;
}

/* REMOVE DEFAULT HEADER */
header {visibility: hidden;}

/* CARD STYLE */
.card {
    background: rgba(255,255,255,0.04);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* BUTTON */
.stButton button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
    font-weight: 500;
}

/* INPUTS */
textarea, input {
    background-color: rgba(255,255,255,0.05) !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* LABELS */
label {
    color: #9ca3af !important;
}

/* TITLE */
.title {
    font-size: 32px;
    font-weight: 600;
}

/* SUBTEXT */
.subtitle {
    color: #9ca3af;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# STATE
# -----------------------------
if "steps" not in st.session_state:
    st.session_state.steps = []

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="title">⚡ Agent-OS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Workflow Builder</div>', unsafe_allow_html=True)

# -----------------------------
# GLOBAL INPUT
# -----------------------------
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    global_input = st.text_area("Global Input", placeholder="Enter your base input...")

    run = st.button("▶ Run Workflow")

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# ADD STEP BUTTON
# -----------------------------
col1, col2 = st.columns([1,6])
with col1:
    if st.button("+ Add Step"):
        st.session_state.steps.append({
            "name": f"Step {len(st.session_state.steps)+1}",
            "prompt": "",
            "model": "gemini-pro"
        })

# -----------------------------
# STEPS UI (CARD BASED)
# -----------------------------
for i, step in enumerate(st.session_state.steps):
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns([6,1])

        with col1:
            step["name"] = st.text_input("Step Name", step["name"], key=f"name_{i}")
        with col2:
            if st.button("✕", key=f"del_{i}"):
                st.session_state.steps.pop(i)
                st.rerun()

        step["prompt"] = st.text_area(
            "Prompt",
            step["prompt"],
            placeholder="Write your instruction...",
            key=f"prompt_{i}"
        )

        step["model"] = st.selectbox(
            "Model",
            ["gemini-pro", "gemini-1.5-pro"],
            key=f"model_{i}"
        )

        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# RUN LOGIC (SIMULATION)
# -----------------------------
if run:
    st.markdown("### Output")

    current_input = global_input

    for step in st.session_state.steps:
        # simulate processing
        output = f"[{step['name']}] → Processed: {current_input}"

        st.markdown(f"""
        <div class="card">
        <b>{step['name']}</b><br><br>
        {output}
        </div>
        """, unsafe_allow_html=True)

        current_input = output
