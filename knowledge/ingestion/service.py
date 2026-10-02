
from pathlib import Path

from knowledge.ingestion.models import DocumentChunk
from knowledge.ingestion.pipeline import ingest_file
from knowledge.ingestion.storage import load_chunks, save_chunks, unique_chunks


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
    """Upsert a document by source ID, preserving unrelated sources.

    ``append`` is retained for API compatibility; all writes now preserve
    unrelated sources regardless of its value.
    """
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

    existing = load_chunks(output_path)
    source_chunks = [
        chunk for chunk in existing if chunk.source_id == source_id
    ]
    unique_existing = unique_chunks(existing)
    unchanged = (
        bool(source_chunks)
        and bool(chunks)
        and all(
            chunk.metadata.sha256 == chunks[0].metadata.sha256
            for chunk in source_chunks
        )
        and {
            (chunk.chunk_id, chunk.chunk_index, chunk.text)
            for chunk in source_chunks
        }
        == {
            (chunk.chunk_id, chunk.chunk_index, chunk.text)
            for chunk in chunks
        }
    )

    if unchanged:
        old_metadata = {
            chunk.chunk_id: chunk.metadata.model_dump(
                mode="json", exclude={"retrieved_at"}
            )
            for chunk in source_chunks
        }
        new_metadata = {
            chunk.chunk_id: chunk.metadata.model_dump(
                mode="json", exclude={"retrieved_at"}
            )
            for chunk in chunks
        }
        metadata_changed = old_metadata != new_metadata

        if metadata_changed:
            preserved = [
                chunk
                for chunk in unique_existing
                if chunk.source_id != source_id
            ]
            save_chunks(preserved + chunks, output_path)
        elif len(unique_existing) != len(existing):
            save_chunks(unique_existing, output_path)
        return []

    # Replace this source only; identical hashes under different IDs remain
    # separate records with their own provenance metadata.
    preserved = [
        chunk for chunk in unique_existing if chunk.source_id != source_id
    ]
    save_chunks(preserved + chunks, output_path)
    return chunks
