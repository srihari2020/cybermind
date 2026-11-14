import requests
import json
import os

CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
OUTPUT_FILE = "data/cisa_kev_dataset.jsonl"

print("📡 Fetching Live CISA KEV Catalog...")
response = requests.get(CISA_URL)
data = response.json()

os.makedirs("data", exist_ok=True)
vulnerabilities = data.get("vulnerabilities", [])

print(f"⚙️ Processing {len(vulnerabilities)} high-priority vulnerabilities...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for vuln in vulnerabilities:
        cve = vuln.get("cveID", "Unknown CVE")
        name = vuln.get("vulnerabilityName", "Unknown Vulnerability")
        desc = vuln.get("shortDescription", "No description available.")
        action = vuln.get("requiredAction", "Apply vendor patch.")
        vendor = vuln.get("vendorProject", "Unknown Vendor")

        # Define the exact query a user might type
        user_query = f"Analyze {cve}: {name}"

        # Hardcode the perfect Markdown response structure
        ai_response = (
            f"Welcome to your lesson! **{cve} ({name})** is a known exploited vulnerability in {vendor} products.\n\n"
            "**Ethics**: *Only investigate or test systems you own.*\n\n"
            "### Phase 1: Core Analysis\n"
            f"{desc}\n"
            "1. **Vulnerability Details**:\n"
            f"   * Date Added to CISA: {vuln.get('dateAdded', 'N/A')}\n"
            f"   * Vendor/Project: {vendor}\n\n"
            "### Phase 2: Tactical Mitigation\n"
            "1. **Required Defensive Action**:\n"
            f"   * `{action}`\n"
            "   * This neutralizes the specific exploitation vector.\n"
        )

        # Build the OpenAI/Ollama compatible JSONL chat row
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

print(f"✅ Success! Fast-generated {len(vulnerabilities)} instruction-tuning records to {OUTPUT_FILE}.")
