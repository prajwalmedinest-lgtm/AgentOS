import streamlit as st
import os
import json

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Agent-OS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "steps" not in st.session_state:
    st.session_state.steps = []

if "workflow_name" not in st.session_state:
    st.session_state.workflow_name = "Untitled Workflow"

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False

# ---------------------------
# UI STYLING
# ---------------------------
st.markdown("""
<style>
html, body {
    font-family: Inter, sans-serif;
}
.stApp {
    background: #0e1117;
    color: #e6e6e6;
}
header {visibility: hidden;}

.title {
    font-size: 34px;
    font-weight: 600;
}
.subtitle {
    color: #9ca3af;
    margin-bottom: 25px;
}

.card {
    background: #161b22;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
    border: 1px solid #2a2f3a;
}

textarea, input, select {
    background-color: #0e1117 !important;
    color: #e6e6e6 !important;
    border-radius: 8px !important;
    border: 1px solid #2a2f3a !important;
}

.stButton button {
    background: #2563eb;
    border-radius: 8px;
    border: none;
    color: white;
    padding: 8px 16px;
}
.stButton button:hover {
    background: #1d4ed8;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
st.markdown('<div class="title">⚡ Agent-OS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Workflow Builder</div>', unsafe_allow_html=True)

# ---------------------------
# API KEY INPUT (NO DOTENV)
# ---------------------------
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns([6,1])

    with col1:
        if not st.session_state.api_key_set:
            api_input = st.text_input(
                "Enter Gemini API Key",
                type="password",
                placeholder="Paste your API key..."
            )
        else:
            st.success("API Key loaded securely")

    with col2:
        if not st.session_state.api_key_set:
            if st.button("Save Key"):
                if api_input:
                    st.session_state.api_key = api_input
                    st.session_state.api_key_set = True
                    st.rerun()
        else:
            if st.button("Reset"):
                st.session_state.api_key = ""
                st.session_state.api_key_set = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# TOP BAR
# ---------------------------
col1, col2, col3 = st.columns([4,1,1])

with col1:
    st.session_state.workflow_name = st.text_input(
        "Workflow Name",
        st.session_state.workflow_name
    )

with col2:
    if st.button("Export"):
        data = {
            "name": st.session_state.workflow_name,
            "steps": st.session_state.steps
        }
        st.download_button(
            "Download JSON",
            data=json.dumps(data, indent=2),
            file_name="workflow.json"
        )

with col3:
    uploaded = st.file_uploader("Import", type="json")
    if uploaded:
        data = json.load(uploaded)
        st.session_state.steps = data.get("steps", [])
        st.session_state.workflow_name = data.get("name", "Imported Workflow")
        st.rerun()

# ---------------------------
# GLOBAL INPUT
# ---------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

global_input = st.text_area(
    "Global Input",
    placeholder="This input flows through all steps..."
)

run_workflow = st.button("▶ Run Workflow")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# ADD STEP
# ---------------------------
if st.button("+ Add Step"):
    st.session_state.steps.append({
        "name": f"Step {len(st.session_state.steps)+1}",
        "prompt": "",
        "model": "gemini-pro"
    })
    st.rerun()

# ---------------------------
# STEP UI
# ---------------------------
for i, step in enumerate(st.session_state.steps):
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns([6,1])

    with col1:
        step["name"] = st.text_input(
            "Step Name",
            step["name"],
            key=f"name_{i}"
        )

    with col2:
        if st.button("✕", key=f"delete_{i}"):
            st.session_state.steps.pop(i)
            st.rerun()

    step["prompt"] = st.text_area(
        "Prompt",
        step["prompt"],
        placeholder="Use {{input}} to pass previous output",
        key=f"prompt_{i}"
    )

    step["model"] = st.selectbox(
        "Model",
        ["gemini-pro", "gemini-1.5-pro"],
        key=f"model_{i}"
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# EXECUTION ENGINE
# ---------------------------
def run_step(step, input_text):
    api_key = st.session_state.api_key

    if not api_key:
        return "❌ API key not set"

    prompt = step["prompt"].replace("{{input}}", input_text)

    return f"{step['name']} OUTPUT → {prompt[:200]}"

# ---------------------------
# RUN WORKFLOW
# ---------------------------
if run_workflow:
    if not global_input:
        st.warning("Please enter global input")
        st.stop()

    st.markdown("## Output")

    current = global_input

    for step in st.session_state.steps:
        output = run_step(step, current)

        st.markdown(f"""
        <div class="card">
        <b>{step['name']}</b><br><br>
        {output}
        </div>
        """, unsafe_allow_html=True)

        current = output
