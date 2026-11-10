# Local Semantic Retrieval

CyberMind's retrieval engine is independent of chat models and API services.
It embeds each ingested chunk, searches a local vector index, and reads the
matching full text and provenance back from the existing JSONL knowledge store.

## Architecture

- Embeddings use `sentence-transformers/all-MiniLM-L6-v2`, a compact CPU-capable
  sentence-transformer with 384-dimensional vectors. Model loading is lazy and
  cached for the lifetime of the embedding component.
- `PersistentVectorIndex` stores a versioned JSON index with chunk/source IDs,
  title, publisher, a SHA-256 hash of chunk text, and a normalized vector. It
  does not duplicate chunk text. Writes replace the index atomically.
- Search uses exact cosine similarity over normalized vectors, implemented
  with Python's standard library. Scores range from -1 to 1; larger means more
  similar, and 1 is an identical vector. Scores are ranking signals, not
  calibrated probabilities or evidence that a chunk supports a claim.
- The JSON index is practical for local and small-to-medium stores. A dedicated
  ANN/vector database can replace it behind the index boundary if corpus size
  later makes exact scans too slow.

## Installation (Windows PowerShell)

From the repository root, install a CPU-only PyTorch build and the project
dependencies. No GPU is required:

```powershell
python -m pip install --upgrade pip
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

For tests and development tooling:

```powershell
python -m pip install -r requirements-dev.txt
```

The first real indexing or search operation downloads the configured model from
Hugging Face if it is not already cached. Unit tests use deterministic fake
embeddings and do not download models or access the network.

## Build And Update The Index

Ingest documents with the existing CLI first, then build/update the vector index:

```powershell
$sample = Join-Path $env:TEMP "cybermind-security.md"
@"
Multi-factor authentication reduces account compromise risk by requiring an
additional proof of identity beyond a password.
"@ | Set-Content -Encoding UTF8 $sample

python -m knowledge.ingestion.cli $sample `
  --source-id cybermind-example/security-basics `
  --title "Security Basics" `
  --publisher "CyberMind local example"

python -m knowledge.retrieval.cli index
```

The default paths are `data/processed/knowledge.jsonl` and
`data/processed/knowledge.index.json`. Set `--store` and `--index` to use other
paths:

```powershell
python -m knowledge.retrieval.cli index `
  --store data/processed/knowledge.jsonl `
  --index data/processed/knowledge.index.json
```

Indexing checks each chunk's text hash and reuses vectors when unchanged. New or
changed chunks are embedded; chunks removed from the JSONL store are removed
from the index. Rebuild all vectors with `--rebuild`:

```powershell
python -m knowledge.retrieval.cli index --rebuild
```

Use the same model for index and search. `--rebuild` is required when changing
the model or its vector dimension.

## Search

```powershell
python -m knowledge.retrieval.cli search `
  "How does multi-factor authentication reduce account compromise risk?" `
  --top-k 5
```

Filter weak matches with a cosine threshold between -1 and 1:

```powershell
python -m knowledge.retrieval.cli search "What is multi-factor authentication?" `
  --top-k 5 `
  --min-similarity 0.35
```

Each result prints the score, source ID, chunk ID, title, publisher, and stored
chunk text. An empty index or no matches prints `No matching chunks found.`
Search never generates an answer or citations beyond the metadata on the
retrieved chunk.

## Configuration And Limitations

Override the model with `--model` or the `CYBERMIND_EMBEDDING_MODEL` environment
variable. Override default paths with `--store` / `--index`, or set
`CYBERMIND_KNOWLEDGE_STORE` / `CYBERMIND_VECTOR_INDEX`:

```powershell
$env:CYBERMIND_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
$env:CYBERMIND_KNOWLEDGE_STORE = "data/processed/knowledge.jsonl"
$env:CYBERMIND_VECTOR_INDEX = "data/processed/knowledge.index.json"
```

The embedding model must be downloaded once. Exact search cost grows linearly
with the number of indexed chunks; this is intentionally simple and avoids
database services or a GPU. JSONL remains the source of truth for chunk text and
complete metadata. Re-run `index` after ingestion to synchronize changes.