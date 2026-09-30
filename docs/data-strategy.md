# CyberMind — Data Strategy

## 1. Purpose

This document defines how CyberMind will acquire, validate, transform, store, retrieve, and use cybersecurity data.

The objective is not to collect the largest possible dataset.

The objective is to construct a high-quality, traceable, continuously maintainable cybersecurity knowledge and training ecosystem.

CyberMind will use three primary data systems:

1. Knowledge Data
2. Fine-Tuning Data
3. Evaluation Data

These systems must remain logically separated.

---

# 2. Core Principle

CyberMind will not attempt to encode the entire cybersecurity domain into model weights.

Instead:

Stable knowledge
        ↓
Fine-tuning

Changing knowledge
        ↓
RAG / Knowledge System

External computation
        ↓
Tools

Controlled actions
        ↓
Cyber Lab

Evaluation
        ↓
CyberBench

This separation allows the system to remain accurate, current, and maintainable.

---

# 3. Data Categories

## 3.1 Authoritative Knowledge

Primary sources should include:

- NIST
- MITRE ATT&CK
- MITRE D3FEND
- OWASP
- CWE
- CAPEC
- CVE/NVD
- CISA
- RFC/IETF
- Official vendor security advisories
- Official technical documentation
- Approved academic material
- Approved course material

These sources should receive higher trust priority than arbitrary internet content.

---

# 4. Source Trust Levels

Each source receives a trust classification.

## Tier 1 — Authoritative

Examples:

- Government standards
- Official standards organizations
- Official security frameworks
- Official vulnerability databases
- Official project documentation

Examples:

NIST
MITRE
IETF
NVD
CISA
OWASP

---

## Tier 2 — High-quality technical

Examples:

- Vendor security advisories
- University publications
- Peer-reviewed research
- Established security research organizations

---

## Tier 3 — Community technical material

Examples:

- Technical blogs
- Community documentation
- Conference material
- Expert tutorials

These may be useful but require additional validation.

---

## Tier 4 — Discovery-only

Examples:

- Random blogs
- Social media
- Unverified posts
- Anonymous material

Tier 4 information should not automatically enter training or authoritative knowledge.

It may be used to discover topics that require verification elsewhere.

---

# 5. Source Registry

Every source must be registered.

Example:

{
    "source_id": "nist_csf_2",
    "organization": "NIST",
    "title": "Cybersecurity Framework 2.0",
    "url": "...",
    "source_type": "framework",
    "trust_tier": 1,
    "license": "...",
    "retrieved_at": "...",
    "version": "2.0"
}

Required metadata:

- Source ID
- Organization
- Title
- URL
- Source type
- Trust tier
- Publication date
- Version
- License/usage information
- Retrieval timestamp
- Content hash

---

# 6. Data Provenance

Every important knowledge item must retain provenance.

Example:

Knowledge item
    |
    +-- source_id
    +-- source_url
    +-- document
    +-- section
    +-- publication date
    +-- version
    +-- retrieval date

The system must be able to answer:

"Where did this information come from?"

---

# 7. Knowledge Sources

Initial source categories:

## Cybersecurity frameworks

- NIST CSF
- NIST SP publications
- CIS-related material where licensing permits

## Threat intelligence

- MITRE ATT&CK
- MITRE D3FEND
- STIX/TAXII-compatible authorized sources
- CISA advisories

## Application security

- OWASP
- OWASP Top 10
- OWASP Web Security Testing Guide
- OWASP API Security material

## Vulnerabilities

- CVE
- NVD
- CWE
- CAPEC
- Vendor advisories

## Networking

- RFC Editor
- IETF specifications
- Official protocol documentation

## Cloud

- Official AWS security documentation
- Official Azure security documentation
- Official Google Cloud security documentation

## Operating systems

- Official Linux documentation
- Official Microsoft security documentation

## Programming

- Official language documentation
- Secure coding guidelines
- Approved security standards

## Education

- Approved university material
- Approved course material
- Licensed textbooks
- Licensed training material

---

# 8. Current Information Versus Stable Information

CyberMind will classify knowledge into:

## Stable

Examples:

- OSI model
- TCP fundamentals
- cryptographic concepts
- security principles
- software engineering principles

Stable information may be appropriate for model adaptation.

## Changing

Examples:

- CVEs
- active vulnerabilities
- vendor advisories
- current threat intelligence
- software versions
- security incidents
- evolving attack techniques

Changing information should primarily be handled through the knowledge/RAG system.

---

# 9. Data Pipeline

All external data must pass through:

Source
  ↓
Collection
  ↓
Raw storage
  ↓
Parsing
  ↓
Normalization
  ↓
Cleaning
  ↓
Deduplication
  ↓
Metadata extraction
  ↓
Quality validation
  ↓
Classification
  ↓
Knowledge store / Training generation

Raw data must never be silently overwritten.

---

# 10. Raw Data

Raw source files are stored in:

data/raw/

Example:

data/raw/
├── nist/
├── mitre/
├── owasp/
├── cve/
├── rfc/
├── cisa/
├── vendors/
└── course/

Raw data should preserve the original source representation whenever practical.

---

# 11. Processed Data

Processed data is stored in:

data/processed/

It may contain:

- Clean text
- Structured records
- Metadata
- Sections
- Tables
- Relationships
- Normalized entities

Processed data must retain references to its original source.

---

# 12. Knowledge Documents

Each document should have metadata.

Example:

{
    "document_id": "...",
    "source_id": "...",
    "title": "...",
    "version": "...",
    "published": "...",
    "retrieved": "...",
    "content_hash": "...",
    "language": "en",
    "trust_tier": 1
}

---

# 13. Chunking

Documents will be divided into semantically meaningful units.

Avoid blindly splitting every document into fixed-size chunks.

Preferred hierarchy:

Document
    ↓
Chapter
    ↓
Section
    ↓
Subsection
    ↓
Semantic chunk

Chunks should preserve context.

---

# 14. Embeddings

Knowledge chunks may receive embeddings for semantic retrieval.

Metadata should remain attached to embeddings.

Example:

{
    "chunk_id": "...",
    "document_id": "...",
    "embedding": "...",
    "topic": "authentication",
    "source": "NIST",
    "trust_tier": 1
}

---

# 15. Hybrid Retrieval

CyberMind should not rely exclusively on vector search.

Retrieval should combine:

- Semantic search
- Keyword search
- Metadata filtering
- Structured knowledge graph queries

Conceptually:

Query
  |
  +--> Vector search
  |
  +--> Keyword search
  |
  +--> Knowledge graph
  |
  +--> Metadata filtering
  |
  v
Reranking
  |
  v
Relevant evidence

---

# 16. Knowledge Graph Data

Structured cybersecurity entities may include:

- CVE
- CWE
- CAPEC
- Technique
- Tactic
- Software
- Malware
- Threat actor
- Vulnerability
- Asset
- Protocol
- Control
- Detection
- Mitigation
- Indicator

Relationships may include:

- exploits
- affects
- mitigates
- detects
- implements
- related_to
- part_of
- uses
- targets
- observed_in

---

# 17. Fine-Tuning Data

Raw documents should not automatically become fine-tuning examples.

Instead:

Raw knowledge
    ↓
Curated examples
    ↓
Validation
    ↓
Training dataset

Fine-tuning examples should teach behaviors such as:

- Explanation
- Reasoning
- Classification
- Evidence analysis
- Code review
- Log analysis
- Security assessment
- Incident reasoning
- Tool selection
- Uncertainty expression
- Teaching

---

# 18. Training Example Structure

Preferred format:

{
    "id": "...",
    "domain": "web_security",
    "difficulty": "intermediate",
    "task_type": "security_analysis",
    "instruction": "...",
    "context": "...",
    "evidence": [],
    "expected_reasoning": "...",
    "response": "...",
    "sources": [],
    "safety_class": "authorized_defensive"
}

Not every example needs every field.

---

# 19. Training Data Categories

Training data should contain multiple task types.

## Knowledge

Question → Explanation

## Reasoning

Scenario → Analysis

## Evidence analysis

Evidence → Findings

## Code security

Code → Vulnerability → Remediation

## Log analysis

Logs → Hypothesis → Investigation

## Network analysis

Network evidence → Interpretation

## Incident response

Incident → Investigation plan

## Teaching

Concept → Level-appropriate explanation

## Assessment

Student answer → Evaluation → Feedback

## Tool use

Task → Tool selection → Tool result → Interpretation

---

# 20. Synthetic Data

Synthetic data may be used to increase coverage.

However, synthetic examples must not automatically be treated as ground truth.

Synthetic pipeline:

Generate
    ↓
Validate
    ↓
Filter
    ↓
Human/automated verification
    ↓
Training candidate

Synthetic examples should be compared against authoritative knowledge where possible.

---

# 21. Cyber Lab Data

The Cyber Lab will generate high-value scenario data.

Example:

Environment
    ↓
Scenario configuration
    ↓
Synthetic events
    ↓
Evidence
    ↓
Expected findings
    ↓
Expected investigation path
    ↓
Verification result

This data can be used for:

- Agent training
- Tool-use training
- Evaluation
- Reinforcement/preference experiments

---

# 22. Human Verification

High-impact training examples should receive additional verification.

Verification levels:

L0 — Unverified

L1 — Automated checks

L2 — Source-backed

L3 — Expert-reviewed

Critical evaluation examples should target L3 where practical.

---

# 23. Contradictions

Cybersecurity sources may disagree.

CyberMind must not silently merge contradictory claims.

When contradictions occur:

1. Preserve both sources.
2. Record publication dates.
3. Record versions.
4. Determine whether one is outdated.
5. Prefer authoritative/current information where justified.
6. Preserve uncertainty when unresolved.

---

# 24. Deduplication

The pipeline must detect:

- Exact duplicates
- Near duplicates
- Reproduced articles
- Repeated explanations
- Duplicate CVE descriptions

Deduplication should operate at:

- Document level
- Section level
- Example level

---

# 25. Data Contamination Prevention

Evaluation datasets must never be intentionally included in training.

The pipeline should check for:

- Exact overlap
- Near-duplicate overlap
- Benchmark leakage
- Generated-example leakage

Training and evaluation datasets must have separate storage and access rules.

---

# 26. Dataset Versioning

Datasets must be versioned.

Example:

cybermind-data-v0.1
cybermind-data-v0.2
cybermind-data-v1.0

A model experiment must reference an exact dataset version.

---

# 27. Licensing

Before using external content for training or redistribution:

- Identify license
- Record license metadata
- Determine permitted use
- Determine redistribution restrictions
- Respect attribution requirements
- Exclude material when rights are unclear

The project must not assume that publicly accessible content is automatically free to copy or train on.

---

# 28. Data Quality Scoring

Every training candidate may receive scores for:

- Accuracy
- Relevance
- Completeness
- Source quality
- Clarity
- Freshness
- Duplication risk
- Safety
- Licensing confidence

Example:

{
    "accuracy": 0.98,
    "relevance": 0.95,
    "source_quality": 1.0,
    "freshness": 0.90,
    "safety": 1.0
}

Quality thresholds will be established experimentally.

---

# 29. Fine-Tuning Dataset Strategy

Initial training mixture should be balanced across:

- Fundamentals
- Networking
- Operating systems
- Secure coding
- Cryptography
- Web security
- API security
- IAM
- Cloud
- Vulnerability management
- SOC
- Incident response
- Forensics
- Threat intelligence
- Security architecture
- Threat modeling

The mixture should not simply reflect the quantity of available internet data.

Sampling should be intentional.

---

# 30. Evaluation Dataset

Evaluation data belongs in:

cyberbench/datasets/

It must not be mixed with:

data/training/

Evaluation datasets should contain:

- Knowledge questions
- Reasoning scenarios
- Code tasks
- Log tasks
- Network tasks
- Incident scenarios
- Tool-use scenarios
- Cyber Lab scenarios

---

# 31. RAG Knowledge Store

The knowledge system should eventually contain:

- Vector index
- Keyword index
- Metadata store
- Knowledge graph
- Source registry
- Document store

The retrieval system must return provenance.

Example:

{
    "answer_context": "...",
    "sources": [
        {
            "source_id": "...",
            "title": "...",
            "section": "...",
            "url": "..."
        }
    ]
}

---

# 32. Data Update Pipeline

Changing information should follow:

Scheduled discovery
      ↓
New/changed source detection
      ↓
Download
      ↓
Hash comparison
      ↓
Parsing
      ↓
Validation
      ↓
Knowledge update
      ↓
Retrieval index update
      ↓
Evaluation
      ↓
Optional model retraining

Model weights should not be retrained automatically for every knowledge update.

---

# 33. Data Quality Gates

Data cannot progress to the next stage unless required checks pass.

Example:

Raw
 ↓
Parsing PASS
 ↓
Metadata PASS
 ↓
Deduplication PASS
 ↓
Quality PASS
 ↓
License PASS
 ↓
Training eligibility PASS

Failures should be recorded rather than silently discarded.

---

# 34. Final Data Architecture

                 EXTERNAL SOURCES
                        |
                        v
                  SOURCE REGISTRY
                        |
                        v
                    RAW DATA
                        |
                        v
                  DATA PIPELINE
                        |
          +-------------+-------------+
          |                           |
          v                           v
    KNOWLEDGE STORE             TRAINING DATA
          |                           |
          v                           v
       RAG / KG                  SFT / PEFT
          |                           |
          +-------------+-------------+
                        |
                        v
                     MODEL
                        |
                        v
                   CyberBench

CyberBench remains isolated from training.

---

# 35. Definition of Done

The data system is considered ready for the first training experiment when:

- Source registry exists
- Authoritative sources are identified
- Licensing is documented
- Raw data storage is implemented
- Processing pipeline exists
- Provenance is preserved
- Deduplication exists
- Quality checks exist
- Training/evaluation separation exists
- Dataset versioning exists
- Initial curated training dataset exists
- CyberBench evaluation dataset exists
- RAG architecture is defined
- Data update strategy is defined