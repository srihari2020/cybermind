import streamlit as st
import requests

# 1. Configure the Professional Dark Mode Layout
st.set_page_config(page_title="CyberMind SOC", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    /* Professional SOC styling */
    .stApp { background-color: #0e1117; }
    .intel-box {
        background-color: #161b22;
        border-left: 4px solid #00ff00;
        padding: 20px;
        border-radius: 5px;
        font-family: 'Courier New', Courier, monospace;
        color: #c9d1d9;
        line-height: 1.6;
    }
    h1 { color: #ffffff; font-family: 'Inter', sans-serif; }
    .stTextInput input {
        background-color: #0d1117;
        color: #58a6ff;
        border: 1px solid #30363d;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ CyberMind Intelligence Interface")
st.caption("Tier-3 Local AI Security Analyst | Powered by Qwen2.5-Instruct (V2)")

# 2. Capture User Input
query = st.text_input("Enter Threat Intel Query, Tool, or Incident:", placeholder="e.g., What are the IoCs for SSH Brute Force?")

if query:
    with st.spinner("Analyzing intelligence..."):
        # 3. Query the local Ollama backend via API
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "cybermind-v2",
            "prompt": query,
            "stream": False
        })
        
        if response.status_code == 200:
            intel_text = response.json().get("response", "")
            
            # 4. Render the output beautifully in the custom UI box
            st.markdown("### 🚨 Intelligence Report")
            st.markdown(f"<div class='intel-box'>{intel_text}</div>", unsafe_allow_html=True)
        else:
            st.error(f"Engine Offline. Is Ollama running? Error: {response.text}")
