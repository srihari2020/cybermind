
import json
import os
import tempfile
from pathlib import Path

from knowledge.ingestion.models import DocumentChunk


def _same_chunk_payload(first: DocumentChunk, second: DocumentChunk) -> bool:
    first_record = first.model_dump(mode="json")
    second_record = second.model_dump(mode="json")
    first_record["metadata"].pop("retrieved_at", None)
    second_record["metadata"].pop("retrieved_at", None)
    return first_record == second_record


def unique_chunks(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
    unique: dict[tuple[str, str], DocumentChunk] = {}

    for chunk in chunks:
        key = (chunk.source_id, chunk.chunk_id)
        previous = unique.get(key)
        if previous is not None and not _same_chunk_payload(previous, chunk):
            raise ValueError(
                "Conflicting records share source_id "
                f"{chunk.source_id!r} and chunk_id {chunk.chunk_id!r}"
            )
        unique.setdefault(key, chunk)

    return list(unique.values())


def _write_chunks(chunks: list[DocumentChunk], path: Path) -> None:
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            for chunk in chunks:
                record = chunk.model_dump(mode="json")
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def save_chunks(
    chunks: list[DocumentChunk],
    file_path: str | Path,
    *,
    append: bool = False,
) -> int:
    """Atomically save chunks as JSON Lines and return the unique count."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing = load_chunks(path) if append else []
    existing_keys = {(chunk.source_id, chunk.chunk_id) for chunk in existing}
    records = unique_chunks(existing + chunks)
    _write_chunks(records, path)

    if append:
        return sum(
            (chunk.source_id, chunk.chunk_id) not in existing_keys
            for chunk in records
        )
    return len(records)


def load_chunks(file_path: str | Path) -> list[DocumentChunk]:
    """Load and validate chunks from a JSONL file."""
    path = Path(file_path)

    if not path.exists():
        return []

    chunks = []

    with path.open("rb") as file:
        for line_number, raw_line in enumerate(file, start=1):
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(
                    f"Invalid UTF-8 at line {line_number} in {path}: {exc}"
                ) from exc

            if not line.strip():
                continue

            try:
                record = json.loads(line)
                chunk = DocumentChunk.model_validate(record)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid chunk record at line {line_number} "
                    f"in {path}: {exc}"
                ) from exc

            if chunk.source_id != chunk.metadata.source_id:
                raise ValueError(
                    f"Invalid chunk record at line {line_number} in {path}: "
                    "chunk and metadata source_id values do not match"
                )
            chunks.append(chunk)

    return chunks
