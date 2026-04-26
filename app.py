# app.py
# Agent-OS — Premium Streamlit AI Workflow Builder (fixed, production-ready)

import streamlit as st
import json
import time
from typing import List, Dict

# Optional import guard for Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Agent-OS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- THEME (CLEAN PREMIUM GRADIENT) --------------------
st.markdown("""
<style>

/* ---------- ROOT THEME ---------- */
:root {
    --bg: #0b1220;
    --bg-soft: #0f172a;
    --card: rgba(255,255,255,0.06);
    --border: rgba(255,255,255,0.08);
    --text: #e5e7eb;
    --muted: #9ca3af;
    --accent: #6366f1;
}

/* Background gradient */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #1e293b 0%, #0b1220 40%, #020617 100%);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid var(--border);
}

/* ---------- CARD ---------- */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 18px;
    backdrop-filter: blur(10px);
    transition: 0.2s ease;
}
.card:hover {
    transform: translateY(-2px);
}

/* ---------- BUTTON ---------- */
.stButton>button {
    border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    border: none;
    color: white;
    padding: 10px 16px;
    transition: 0.2s ease;
}
.stButton>button:hover {
    transform: translateY(-1px);
}

/* ---------- INPUTS ---------- */
textarea, input, select {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

/* Titles */
.title {
    font-size: 30px;
    font-weight: 700;
}
.subtitle {
    color: var(--muted);
    margin-bottom: 20px;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "workflow" not in st.session_state:
    st.session_state.workflow: List[Dict] = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "run_outputs" not in st.session_state:
    st.session_state.run_outputs = {}

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# -------------------- GEMINI FUNCTION --------------------
def call_gemini(prompt: str) -> str:
    if not GEMINI_AVAILABLE:
        return "❌ google-generativeai not installed."

    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        # retry once
        try:
            time.sleep(1)
            response = model.generate_content(prompt)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as e2:
            return f"❌ Error: {str(e2)}"

# -------------------- WORKFLOW HELPERS --------------------
def add_step():
    st.session_state.workflow.append({
        "id": int(time.time()*1000),
        "name": f"Step {len(st.session_state.workflow)+1}",
        "model": "Gemini",
        "input": "",
        "output": ""
    })

def reset_workflow():
    st.session_state.workflow = []
    st.session_state.run_outputs = {}

def load_template(name: str):
    if name == "Research Agent":
        st.session_state.workflow = [
            {"id":1,"name":"Analyze Topic","model":"Gemini","input":"Analyze this topic deeply: {{input}}","output":""},
            {"id":2,"name":"Insights","model":"Gemini","input":"Extract insights from: {{prev_output}}","output":""},
            {"id":3,"name":"Summary","model":"Gemini","input":"Summarize: {{prev_output}}","output":""}
        ]

    elif name == "Startup Idea Generator":
        st.session_state.workflow = [
            {"id":1,"name":"Generate Ideas","model":"Gemini","input":"Generate startup ideas for {{input}}","output":""},
            {"id":2,"name":"Refine","model":"Gemini","input":"Refine this: {{prev_output}}","output":""},
            {"id":3,"name":"Pitch","model":"Gemini","input":"Create a pitch: {{prev_output}}","output":""}
        ]

    elif name == "Code Explainer":
        st.session_state.workflow = [
            {"id":1,"name":"Explain","model":"Gemini","input":"Explain this code: {{input}}","output":""},
            {"id":2,"name":"Simplify","model":"Gemini","input":"Simplify: {{prev_output}}","output":""}
        ]

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## ⚡ Agent-OS")

    st.session_state.api_key = st.text_input("Gemini API Key", type="password")

    st.markdown("### Workflow")
    if st.button("➕ Add Step"):
        add_step()

    template = st.selectbox(
        "Templates",
        ["None", "Research Agent", "Startup Idea Generator", "Code Explainer"]
    )
    if st.button("Load Template"):
        load_template(template)

    st.markdown("---")

    # Export
    st.download_button(
        "Export JSON",
        data=json.dumps(st.session_state.workflow, indent=2),
        file_name="agent_os_workflow.json"
    )

    # Import
    uploaded = st.file_uploader("Import JSON", type=["json"])
    if uploaded:
        try:
            st.session_state.workflow = json.load(uploaded)
            st.success("Workflow loaded")
        except:
            st.error("Invalid JSON")

    if st.button("Reset"):
        reset_workflow()

# -------------------- MAIN HEADER --------------------
st.markdown('<div class="title">Agent-OS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Workflow Builder</div>', unsafe_allow_html=True)

# Global Input
st.session_state.user_input = st.text_area(
    "Global Input (used in {{input}})",
    st.session_state.user_input
)

# -------------------- RUN WORKFLOW --------------------
if st.button("▶ Run Workflow"):
    if not st.session_state.workflow:
        st.warning("Add steps first")
    elif not st.session_state.api_key:
        st.warning("Enter API key")
    else:
        prev_output = ""
        st.session_state.run_outputs = {}

        for i, step in enumerate(st.session_state.workflow):
            prompt = step["input"]
            prompt = prompt.replace("{{input}}", st.session_state.user_input)
            prompt = prompt.replace("{{prev_output}}", prev_output)

            with st.spinner(f"Running {step['name']}..."):
                output = call_gemini(prompt)

            prev_output = output
            st.session_state.run_outputs[step["id"]] = {
                "prompt": prompt,
                "output": output
            }

# -------------------- WORKFLOW UI --------------------
for i, step in enumerate(st.session_state.workflow):
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns([5,1])

    with col1:
        step["name"] = st.text_input(
            "Step Name",
            value=step["name"],
            key=f"name_{step['id']}"
        )

        step["input"] = st.text_area(
            "Prompt",
            value=step["input"],
            key=f"input_{step['id']}"
        )

        step["model"] = st.selectbox(
            "Model",
            ["Gemini", "OpenAI", "Claude"],
            key=f"model_{step['id']}"
        )

    with col2:
        if st.button("Delete", key=f"del_{step['id']}"):
            st.session_state.workflow.pop(i)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- OUTPUT --------------------
st.markdown("## Results")

for step in st.session_state.workflow:
    if step["id"] in st.session_state.run_outputs:
        data = st.session_state.run_outputs[step["id"]]

        with st.expander(step["name"]):
            st.markdown("**Prompt**")
            st.code(data["prompt"])

            st.markdown("**Output**")
            st.write(data["output"])
