# CyberMind — Development Notes & Changelog

## Project Genesis
**Goal:** Build a small, efficient, domain-specialized cybersecurity AI model delivering high-quality cybersecurity analysis, answers, and threat detection.
**Architecture:** A hybrid intelligence system combining Traditional ML (for high-speed telemetry classification), a Retrieval-Augmented Generation (RAG) engine (for ground-truth knowledge), and a specialized Local LLM (for reasoning).

---

## Phase 1: Project Foundation (Completed)

**Objective:** Establish a reliable, tested development and experimentation environment.

1. **Repository Setup:**
   - Initialized the Git repository and built the core directory structure (`backend`, `knowledge`, `ml`, `docs`, `tests`, `scripts`).
   - Defined the **Master Capability Matrix** (`capability-matrix.md`) mapping 19 cybersecurity domains across 7 maturity levels (L0-L6).
   - Defined the **Master Development Roadmap** (`roadmap.md`) outlining the 10 phases from foundation to open-source publication.

2. **Core Backend & Virtual Environment:**
   - Configured `pyproject.toml` with strict, minimal dependencies (PyTorch, SentenceTransformers, Pydantic, FastAPI).
   - Established the Python virtual environment (`.venv`).
   - Built `backend/config.py` with automatic hardware detection for CUDA (PyTorch).

3. **Phase 1 Codebase & Tests:**
   - Implemented `knowledge/ingestion/pipeline.py` to chunk text documents efficiently using SHA-256 hashing.
   - Built `knowledge/retrieval/index.py`, a `PersistentVectorIndex` to securely store vectors and metadata in a JSON format.
   - Successfully executed `pytest`, achieving **78 passing tests** that validated the initial architecture.

4. **Git Crisis & Resolution:**
   - Encountered a Git rebase conflict while attempting to correct author email attribution (`sriharimadavi@gmail.com`).
   - Successfully aborted the dangerous rebase and utilized `git commit-tree` to seamlessly rewrite the commit history while mathematically preserving the original file trees (CUDA and retrieval implementations remained untouched).
   - Force-pushed the corrected history safely using `--force-with-lease`.

---

## Phase 2: Cybersecurity Dataset Collection (In Progress)

**Objective:** Build a high-quality cybersecurity dataset foundation with strict provenance and licensing.

1. **Securing the Data Directory:**
   - Appended `data/` to `.gitignore` to guarantee raw and processed datasets (gigabytes of data) are never accidentally pushed to GitHub.

2. **Dataset Registry (`knowledge/ingestion/registry.py`):**
   - Built a custom `DatasetRegistry` to formally track the source, URL, license, and SHA-256 checksum of every dataset entering the CyberMind pipeline.
   - Successfully downloaded the **CISA Known Exploited Vulnerabilities (KEV)** JSON catalog.
   - Successfully downloaded the **MITRE ATT&CK Enterprise STIX 2.1** framework.
   - Verified the integrity of downloads by generating SHA-256 provenance manifests in `data/manifests/`.

3. **Data Parsers (`knowledge/ingestion/parsers.py`):**
   - Wrote specific parsers to extract intelligence from raw JSON feeds.
   - Successfully parsed **1,779** CISA KEV vulnerabilities.
   - Successfully parsed **867** MITRE ATT&CK Enterprise techniques.

4. **Building the RAG Vector Index (`scripts/build_vector_index.py`):**
   - Integrated the parsers with the Hugging Face `SentenceTransformers` library.
   - Leveraged the Legion RTX GPU (via CUDA) to embed all 2,646 cybersecurity records using the `BAAI/bge-small-en-v1.5` model.
   - Saved the resulting 384-dimensional vectors into the `PersistentVectorIndex` at `data/processed/knowledge.index.json`.

5. **Semantic Search Validation (`scripts/test_search.py`):**
   - Built a query script to test mathematical retrieval.
   - **Query 1:** *"What is Log4Shell?"* successfully matched MITRE application vulnerability techniques (e.g., T1004).
   - **Query 2:** *"How do attackers abuse scheduled tasks in Windows?"* successfully matched **MITRE T1053.005** (Scheduled Task/Job) and **CVE-2024-49039** (Windows Task Scheduler vulnerability) with >0.82 similarity scores.
   - Proved the foundational RAG engine works perfectly and is ready to ground a language model in factual truth.
