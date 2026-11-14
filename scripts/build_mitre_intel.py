import requests
import json
import os

MITRE_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
OUTPUT_FILE = "data/mitre_attack_dataset.jsonl"

print("📡 Fetching Live MITRE ATT&CK Enterprise Framework...")
response = requests.get(MITRE_URL)
data = response.json()

objects = data.get("objects", [])
# Filter for active attack patterns only
techniques = [obj for obj in objects if obj.get("type") == "attack-pattern" and not obj.get("revoked") and not obj.get("x_mitre_deprecated")]

print(f"⚙️ Processing {len(techniques)} Enterprise Techniques...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for tech in techniques:
        name = tech.get("name", "Unknown Technique")
        desc = tech.get("description", "No description available.")
        
        # Truncate description to keep model memory efficient
        if len(desc) > 800:
            desc = desc[:797] + "..."
            
        # Extract the T-Code (e.g., T1566)
        ext_refs = tech.get("external_references", [])
        mitre_id = next((ref.get("external_id") for ref in ext_refs if ref.get("source_name") == "mitre-attack"), "TXXXX")

        user_query = f"Explain MITRE ATT&CK Technique {mitre_id}: {name}"

        ai_response = (
            f"Welcome to your lesson! **{mitre_id} ({name})** is a recognized MITRE ATT&CK adversary technique.\n\n"
            "**Ethics**: *Only investigate or test systems you own.*\n\n"
            "### Phase 1: Core Analysis\n"
            f"{desc}\n"
            "1. **Technique Identification**:\n"
            f"   * MITRE ID: {mitre_id}\n"
            f"   * Tactic Type: Enterprise Attack Pattern\n\n"
            "### Phase 2: Tactical Mitigation\n"
            "1. **Defensive Action**:\n"
            "   * `Deploy behavioral analytics and endpoint telemetry`\n"
            "   * Monitor process executions and network anomalies associated with this technique.\n"
        )

        row = {
            "messages": [
                {
                    "role": "system", 
                    "content": "You are CyberMind, an expert Tier-3 SOC Analyst. You MUST format your response using EXACTLY this Markdown structure."
                },
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": ai_response}
            ]
        }
        
        f.write(json.dumps(row) + "\n")

print(f"✅ Success! Fast-generated {len(techniques)} instruction-tuning records to {OUTPUT_FILE}.")
