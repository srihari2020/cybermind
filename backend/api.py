from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import uvicorn
import logging

# Set up logging for the SOC dashboard
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PacketRouter")

app = FastAPI(title="CyberMind Packet Intelligence", version="1.0")

# --- DATA MODELS ---
class PacketData(BaseModel):
    source_ip: str
    dest_ip: str
    port: int
    protocol: str
    packet_size: int
    tcp_flags: int

class ClassificationResult(BaseModel):
    status: str
    confidence: float
    threat_type: str

# --- PLACEHOLDER FOR SCIKIT-LEARN MODEL ---
# In the next step, we will replace this with joblib.load('rf_model.pkl')
def predict_packet(features: list) -> dict:
    """
    Simulates the Random Forest classification. 
    Flags packets targeting port 22 (SSH) or 3389 (RDP) with large sizes as suspicious.
    """
    port = features[2]
    size = features[4]
    
    if port in [22, 3389] and size > 1500:
        return {"status": "MALICIOUS", "confidence": 0.94, "threat_type": "Data Exfiltration / Brute Force"}
    return {"status": "BENIGN", "confidence": 0.99, "threat_type": "None"}

# --- ENDPOINTS ---
@app.post("/analyze_packet", response_model=ClassificationResult)
async def analyze_packet(packet: PacketData):
    try:
        # Convert incoming JSON into a feature array for Scikit-Learn
        # (Assuming protocol is converted to a dummy int for this example)
        protocol_int = 6 if packet.protocol.upper() == "TCP" else 17
        features = [
            0, # IP string conversion placeholder
            0, # IP string conversion placeholder
            packet.port,
            protocol_int,
            packet.packet_size,
            packet.tcp_flags
        ]
        
        # Run inference
        result = predict_packet(features)
        
        if result["status"] == "MALICIOUS":
            logger.warning(f"🚨 THREAT DETECTED: {packet.source_ip} -> {packet.dest_ip}:{packet.port}")
            
        return result
        
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        raise HTTPException(status_code=500, detail="Packet analysis failed")

@app.get("/health")
async def health_check():
    return {"engine": "online", "model": "RandomForest_v1"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
