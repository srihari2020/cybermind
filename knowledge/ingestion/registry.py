import hashlib
import json
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


@dataclass
class DatasetSource:
    id: str
    name: str
    url: str
    category: str  # 'knowledge' or 'ml'
    relative_path: str
    license: str


# The official CyberMind Phase 2 Dataset Registry
CYBERMIND_DATASETS: Dict[str, DatasetSource] = {
    "cisa_kev": DatasetSource(
        id="cisa_kev",
        name="CISA Known Exploited Vulnerabilities",
        url="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        category="knowledge",
        relative_path="raw/knowledge/cisa/known_exploited_vulnerabilities.json",
        license="Public Domain",
    ),
    "mitre_enterprise": DatasetSource(
        id="mitre_enterprise",
        name="MITRE ATT&CK Enterprise STIX",
        url="https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json",
        category="knowledge",
        relative_path="raw/knowledge/mitre_attack/enterprise-attack.json",
        license="Apache-2.0 / MITRE Terms",
    ),
}


class DatasetRegistry:
    def __init__(self, base_dir: Path = Path("data")):
        self.base_dir = base_dir
        self.manifest_dir = base_dir / "manifests"
        self.manifest_dir.mkdir(parents=True, exist_ok=True)

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculates the SHA-256 checksum of a file to ensure data integrity."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def download_dataset(self, dataset_id: str) -> dict:
        """Downloads a dataset from the registry and records its provenance manifest."""
        if dataset_id not in CYBERMIND_DATASETS:
            raise ValueError(f"Dataset {dataset_id} not found in registry.")

        source = CYBERMIND_DATASETS[dataset_id]
        target_path = self.base_dir / source.relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Downloading {source.name}...")
        
        req = urllib.request.Request(source.url, headers={'User-Agent': 'CyberMind-Data-Pipeline/1.0'})
        with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
            out_file.write(response.read())

        file_hash = self._calculate_sha256(target_path)
        file_size = target_path.stat().st_size

        provenance = {
            "dataset_id": source.id,
            "name": source.name,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "source_url": source.url,
            "license": source.license,
            "sha256": file_hash,
            "size_bytes": file_size,
            "local_path": str(target_path)
        }

        manifest_path = self.manifest_dir / f"{source.id}_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(provenance, f, indent=2)

        print(f"Success! Saved to {target_path} (SHA256: {file_hash[:8]}...)")
        return provenance
