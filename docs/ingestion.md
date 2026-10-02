# Local Document Ingestion

The ingestion CLI reads local UTF-8 `.txt` and `.md` files, normalizes their
text, splits it into overlapping character-based chunks, attaches provenance
metadata, and writes JSONL records. It does not fetch URLs or execute document
content.

## Ingest One Document

Run from the repository root and provide a stable source ID, a title, and the
publisher that accurately describes the document's provenance:

```powershell
python -m knowledge.ingestion.cli data/raw/security.md `
  --source-id cybermind-example/security-basics `
  --title "Security Basics" `
  --publisher "CyberMind local example"
```

The default output is `data/processed/knowledge.jsonl`. Set `--output` to use
another JSONL file. Existing sources in that output are preserved by default.

## Ingest a Directory

Directories are searched recursively. Files are processed in sorted relative
path order, and failures are reported while processing continues:

```powershell
python -m knowledge.ingestion.cli data/raw `
  --publisher "CyberMind local example" `
  --source-id cybermind-local-batch
```

Each batch source ID is `batch:<namespace>/<relative-path>`, with path
separators normalized to `/`. The namespace is the directory's name unless
`--source-id` supplies one. Relative paths distinguish duplicate filenames in
different subdirectories. Reuse the same namespace and relative path to update
that document on later runs. Choose a distinct namespace when ingesting a
different directory tree that could contain the same relative paths; otherwise
those paths intentionally resolve to the same source identities.

## Identity And Duplicates

`source_id` identifies provenance, not content. A single-file caller chooses
it explicitly; batch mode derives it from a stable namespace and relative
path. Ingestion replaces chunks only for that source ID, preserving unrelated
sources. Identical bytes with different source IDs remain separate documents,
with independent metadata; content hashes are never used to merge provenance.

SHA-256 is calculated over the original file bytes. Re-ingesting unchanged
content for the same source ID skips chunk creation when its chunk layout is
unchanged. A changed document or chunk layout replaces that source's records.
Exact legacy duplicate rows are cleaned up, allowing a different
`retrieved_at` timestamp; conflicting records with the same source and chunk
IDs fail instead of choosing metadata silently. `--append` remains accepted
for CLI compatibility; writes now always preserve unrelated sources.

## Limitations

- Only local UTF-8 `.txt` and `.md` files are supported; PDF, HTML, OCR, and
  remote fetching are not implemented.
- Chunks are sized by characters and prefer whitespace boundaries; semantic
  section-aware splitting and embeddings are future work.
- JSONL replacement is atomic per write, but simultaneous writers are not
  coordinated. Use a single ingestion process per output file.
- The repository's `data/raw/security.md` is a generic project sample, not an
  official NIST publication. Set publisher metadata from verified provenance;
  do not infer it from the subject matter.