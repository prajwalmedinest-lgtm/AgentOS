# app.py

import streamlit as st
import json
import time
import google.generativeai as genai

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Agent-OS", layout="wide")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
/* Background */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #020617;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Card UI */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 18px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    transition: all 0.2s ease;
}

.card:hover {
    transform: translateY(-2px);
    border: 1px solid rgba(255,255,255,0.15);
}

/* Buttons */
.stButton>button {
    border-radius: 12px;
    padding: 10px 16px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    transition: 0.2s ease;
}

.stButton>button:hover {
    transform: scale(1.03);
    opacity: 0.9;
}

/* Inputs */
textarea, input {
    border-radius: 10px !important;
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
}

/* Header */
.title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 10px;
}

.subtitle {
    color: #94a3b8;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "workflow" not in st.session_state:
    st.session_state.workflow = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# -------------------- GEMINI SETUP --------------------
def call_gemini(prompt):
    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Retry once
        try:
            time.sleep(1)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## ⚡ Agent-OS")

    st.session_state.api_key = st.text_input("Gemini API Key", type="password")

    if st.button("➕ Add Step"):
        st.session_state.workflow.append({
            "id": len(st.session_state.workflow),
            "name": f"Step {len(st.session_state.workflow)+1}",
            "model": "Gemini",
            "input": "",
            "output": ""
        })

    # -------- Templates --------
    template = st.selectbox("Load Template", ["None", "Research Agent", "Startup Idea Generator", "Code Explainer"])

    if st.button("Apply Template"):
        if template == "Research Agent":
            st.session_state.workflow = [
                {"id":0,"name":"Topic Analysis","model":"Gemini","input":"Analyze {{input}} deeply","output":""},
                {"id":1,"name":"Key Insights","model":"Gemini","input":"Extract key insights from {{prev_output}}","output":""},
                {"id":2,"name":"Summary","model":"Gemini","input":"Summarize {{prev_output}}","output":""}
            ]

        elif template == "Startup Idea Generator":
            st.session_state.workflow = [
                {"id":0,"name":"Idea Generation","model":"Gemini","input":"Generate startup ideas for {{input}}","output":""},
                {"id":1,"name":"Validation","model":"Gemini","input":"Validate {{prev_output}}","output":""},
                {"id":2,"name":"Pitch","model":"Gemini","input":"Create pitch for {{prev_output}}","output":""}
            ]

        elif template == "Code Explainer":
            st.session_state.workflow = [
                {"id":0,"name":"Explain Code","model":"Gemini","input":"Explain this code: {{input}}","output":""},
                {"id":1,"name":"Simplify","model":"Gemini","input":"Simplify explanation: {{prev_output}}","output":""}
            ]

    # -------- Export --------
    st.download_button(
        "Export Workflow",
        json.dumps(st.session_state.workflow, indent=2),
        file_name="workflow.json"
    )

    # -------- Import --------
    uploaded_file = st.file_uploader("Import Workflow")
    if uploaded_file:
        st.session_state.workflow = json.load(uploaded_file)

    # -------- Reset --------
    if st.button("Reset"):
        st.session_state.workflow = []

# -------------------- MAIN UI --------------------
st.markdown('<div class="title">🚀 Agent-OS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Build AI workflows visually</div>', unsafe_allow_html=True)

# -------------------- RUN WORKFLOW --------------------
if st.button("▶ Run Workflow"):
    if not st.session_state.workflow:
        st.warning("⚠️ Add steps before running.")
    elif not st.session_state.api_key:
        st.warning("⚠️ Enter API key.")
    else:
        prev_output = ""
        for step in st.session_state.workflow:
            prompt = step["input"].replace("{{prev_output}}", prev_output)

            output = call_gemini(prompt)

            step["output"] = output
            prev_output = output

# -------------------- WORKFLOW CARDS --------------------
for i, step in enumerate(st.session_state.workflow):
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns([4,1])

        with col1:
            step["name"] = st.text_input("Step Name", step["name"], key=f"name_{i}")
            step["input"] = st.text_area("Prompt", step["input"], key=f"input_{i}")

            step["model"] = st.selectbox(
                "Model",
                ["Gemini", "OpenAI", "Claude"],
                index=0,
                key=f"model_{i}"
            )

        with col2:
            if st.button("🗑 Delete", key=f"delete_{i}"):
                st.session_state.workflow.pop(i)
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- OUTPUT DISPLAY --------------------
st.markdown("## 📊 Results")

for step in st.session_state.workflow:
    if step["output"]:
        with st.expander(step["name"]):
            st.markdown("**Prompt:**")
            st.code(step["input"])

            st.markdown("**Output:**")
            st.write(step["output"])
