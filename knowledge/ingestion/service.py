
from pathlib import Path

from knowledge.ingestion.models import DocumentChunk
from knowledge.ingestion.pipeline import ingest_file
from knowledge.ingestion.storage import save_chunks


def ingest_and_save(
    file_path: str | Path,
    output_path: str | Path,
    *,
    source_id: str,
    title: str,
    publisher: str,
    source_url: str | None = None,
    license: str | None = None,
    chunk_size: int = 800,
    overlap: int = 120,
    append: bool = False,
) -> list[DocumentChunk]:
    """Ingest a document, persist its chunks, and return them."""
    chunks = ingest_file(
        file_path,
        source_id=source_id,
        title=title,
        publisher=publisher,
        source_url=source_url,
        license=license,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    save_chunks(
        chunks,
        output_path,
        append=append,
    )

    return chunks
