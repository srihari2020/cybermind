import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="CyberMind Unified Intelligence API")

# 1. Load the ML Engine (Scikit-Learn)
try:
    ml_model = joblib.load("model/ml_engine/network_rf_model.pkl")
    print("✅ Traditional ML Engine loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load ML model: {e}")

# 2. Connect the LLM Engine (Ollama/Qwen)
llm_client = OpenAI(base_url="http://localhost:11434/v1", api_key="cybermind-local")
LLM_MODEL = "qwen3.5:4b"

# 3. Define the incoming Network Telemetry data structure
class NetworkTelemetry(BaseModel):
    packet_size: float
    destination_port: int
    connection_duration: float
    failed_logins: int
    bytes_transferred: float

@app.post("/api/analyze_traffic")
async def analyze_traffic(data: NetworkTelemetry):
    # STEP A: ML Engine analyzes the raw numbers in less than a millisecond
    features = np.array([[
        data.packet_size,
        data.destination_port,
        data.connection_duration,
        data.failed_logins,
        data.bytes_transferred
    ]])
    
    prediction = ml_model.predict(features)[0]
    is_malicious = bool(prediction == 1)
    
    # If the ML Engine says it's safe, we return instantly without waking up the LLM
    if not is_malicious:
        return {
            "status": "SAFE",
            "alert": "Normal traffic patterns detected.",
            "incident_report": None
        }
        
    # STEP B: If Malicious, the Orchestration Layer triggers the LLM for analysis
    threat_context = (
        f"Anomaly detected! Destination Port: {data.destination_port}, "
        f"Failed Logins: {data.failed_logins}, Packet Size: {data.packet_size} bytes."
    )
    
    system_prompt = "You are CyberMind, an expert AI Security Analyst. Write a highly technical, concise incident response report."
    user_prompt = (
        f"Network Telemetry Alert: {threat_context}\n\n"
        "Task: Identify the likely MITRE ATT&CK technique (e.g., Brute Force, Exfiltration) based on these metrics, "
        "and recommend three immediate mitigation steps for the firewall."
    )
    
    # Generate the report
    try:
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        incident_report = response.choices[0].message.content.strip()
    except Exception as e:
        incident_report = f"LLM Generation Failed: {str(e)}"
        
    # STEP C: Return the Unified Response
    return {
        "status": "CRITICAL_ALERT",
        "alert": "Malicious attack detected by ML Engine.",
        "incident_report": incident_report
    }
