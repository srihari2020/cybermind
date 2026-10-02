
import hashlib
import re
from pathlib import Path

from knowledge.ingestion.models import DocumentChunk, DocumentMetadata


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def calculate_sha256(content: bytes) -> str:
    """Calculate the SHA-256 hash of the original file content."""
    return hashlib.sha256(content).hexdigest()


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_chunks(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[str]:
    """Split text into overlapping chunks, preferring word boundaries."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    text = normalize_text(text)

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            boundary = text.rfind(" ", start, end)

            if boundary > start + overlap:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = end - overlap
        start = max(next_start, start + 1)

    return chunks


def ingest_file(
    file_path: str | Path,
    *,
    source_id: str,
    title: str,
    publisher: str,
    source_url: str | None = None,
    license: str | None = None,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[DocumentChunk]:
    """Read a local text document and convert it into metadata-linked chunks."""
    path = Path(file_path)

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {path.suffix}. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    content = path.read_bytes()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Document must use UTF-8 encoding"
        ) from exc

    normalized_text = normalize_text(text)

    if not normalized_text:
        raise ValueError("Document is empty")

    metadata = DocumentMetadata(
        source_id=source_id,
        title=title,
        publisher=publisher,
        source_url=source_url,
        license=license,
        sha256=calculate_sha256(content),
    )

    text_chunks = split_into_chunks(
        normalized_text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return [
        DocumentChunk(
            chunk_id=f"{source_id}-{index:04d}",
            source_id=source_id,
            chunk_index=index,
            text=chunk,
            metadata=metadata,
        )
        for index, chunk in enumerate(text_chunks)
    ]
