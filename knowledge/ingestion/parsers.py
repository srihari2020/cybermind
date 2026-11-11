import json
from pathlib import Path
from typing import List, Dict, Any


def parse_cisa_kev(file_path: Path) -> List[Dict[str, Any]]:
    """Extracts vulnerabilities from the CISA KEV JSON catalog."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    documents = []
    for vuln in data.get("vulnerabilities", []):
        cve_id = vuln.get("cveID", "Unknown")
        name = vuln.get("vulnerabilityName", "")
        desc = vuln.get("shortDescription", "")
        action = vuln.get("requiredAction", "")
        
        text = f"CVE: {cve_id}\nName: {name}\nDescription: {desc}\nRequired Action: {action}"
        documents.append({
            "source_id": cve_id,
            "source_type": "cisa_kev",
            "content": text
        })
    return documents


def parse_mitre_enterprise(file_path: Path) -> List[Dict[str, Any]]:
    """Extracts attack patterns (techniques) from MITRE ATT&CK STIX 2.1."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    documents = []
    for obj in data.get("objects", []):
        if obj.get("type") == "attack-pattern":
            name = obj.get("name", "")
            desc = obj.get("description", "")
            
            # Extract MITRE ID (e.g., T1566)
            mitre_id = "Unknown"
            for ext in obj.get("external_references", []):
                if ext.get("source_name") == "mitre-attack":
                    mitre_id = ext.get("external_id", "Unknown")
                    break
                    
            text = f"MITRE ATT&CK ID: {mitre_id}\nTechnique: {name}\nDescription: {desc}"
            documents.append({
                "source_id": mitre_id,
                "source_type": "mitre_enterprise",
                "content": text
            })
    return documents
