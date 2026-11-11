# CyberMind — Complete Development Notes & Changelog

## Project Genesis & Architecture
**Goal:** Build a small, efficient, domain-specialized cybersecurity AI model delivering high-quality analysis, answers, and threat detection.
**Architecture:** A hybrid intelligence system combining Traditional ML (for high-speed telemetry classification), a Retrieval-Augmented Generation (RAG) engine (for ground-truth knowledge), and a specialized Local LLM (for reasoning).

---

## Phase 1: Project Foundation (Completed)

**Objective:** Establish a reliable, tested development and experimentation environment.

* **Repository Setup:** 
  * Initialized Git repository and built the core directory structure (`backend`, `knowledge`, `ml`, `docs`, `tests`, `scripts`, `data`).
  * Defined the **Master Capability Matrix** (`capability-matrix.md`) mapping 19 cybersecurity domains across 7 maturity levels.
  * Defined the **Master Development Roadmap** (`roadmap.md`).
* **Core Backend & Virtual Environment:**
  * Configured `pyproject.toml` with strict dependencies (PyTorch, SentenceTransformers, FastAPI).
  * Established the Python virtual environment (`.venv`) and configured `backend/config.py` for automatic CUDA detection on the RTX 5060.
* **Phase 1 Codebase & Tests:**
  * Implemented `knowledge/ingestion/pipeline.py` (SHA-256 chunking) and `knowledge/retrieval/index.py` (`PersistentVectorIndex`).
  * Successfully passed **78 initial architecture tests** using `pytest`.
* **Git Crisis & Resolution:**
  * Encountered a Git rebase conflict correcting author email attribution.
  * Safely used a `git commit-tree` bash script to rewrite history while mathematically preserving original file trees, force-pushing with `--force-with-lease`.

---

## Phase 2: Cybersecurity Dataset Collection (Completed)

**Objective:** Build a high-quality cybersecurity dataset foundation with strict provenance.

* **Securing the Data Directory:** Appended `data/` to `.gitignore` to prevent gigabytes of data from leaking into the Git history.
* **Dataset Registry (`knowledge/ingestion/registry.py`):**
  * Built a formal `DatasetRegistry` tracking source, URL, license, and SHA-256 checksums.
  * Downloaded **CISA Known Exploited Vulnerabilities (KEV)** and **MITRE ATT&CK Enterprise STIX 2.1**.
* **Data Parsers (`knowledge/ingestion/parsers.py`):**
  * Parsed raw JSON into clean text chunks: **1,779** CISA KEV vulnerabilities and **867** MITRE techniques (2,646 total records).

---

## Phase 6 & 7: RAG Engine & Local LLM API Integration (Completed)

**Objective:** Give CyberMind access to verifiable knowledge and bridge it with a fast, local API reasoning engine.

* **Building the RAG Vector Index (`scripts/build_vector_index.py`):**
  * Leveraged the RTX 5060 GPU to embed all 2,646 records using `BAAI/bge-small-en-v1.5`.
  * Saved the 384-dimensional vectors into `data/processed/knowledge.index.json`.
* **Semantic Search & Context Window Optimization (`scripts/test_rag_generation.py`):**
  * Solved the "Dense Retrieval Exact Match" issue by adding the BGE-specific prefix (`Represent this sentence...`) and querying semantically instead of using raw CVE IDs.
  * Discovered a GPU Context Window Overflow issue when feeding massive MITRE records to the LLM. Solved by implementing a strict 1000-character truncation safety limit.
* **Local LLM Environment Setup:**
  * Bypassed Ubuntu's PEP 668 system-wide package block by bootstrapping `pip` directly into the `.venv`.
  * Installed the `openai` Python client to route prompts locally to Ollama running `qwen3.5:4b`.
  * Verified anti-hallucination guardrails: the LLM successfully refused to answer when fed irrelevant documents.
* **FastAPI Backend Server (`backend/api/main.py`):**
  * Wrapped the RAG search and Qwen generation into a production-grade FastAPI server.
  * Implemented `@asynccontextmanager lifespan` to lock the ML embedding model and OpenAI client into VRAM/RAM at startup, enabling millisecond response times.
  * Successfully validated the API via a `curl` POST request. CyberMind correctly explained "Pass the Hash", identified the Windows KB update, and cited MITRE T1550.002 in a clean JSON payload.
