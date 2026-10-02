
import json
from pathlib import Path

from knowledge.ingestion.models import DocumentChunk


def save_chunks(
    chunks: list[DocumentChunk],
    file_path: str | Path,
    *,
    append: bool = False,
) -> int:
    """Save document chunks as JSON Lines and return the number saved."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    mode = "a" if append else "w"
    count = 0

    with path.open(mode, encoding="utf-8") as file:
        for chunk in chunks:
            record = chunk.model_dump(mode="json")
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count


def load_chunks(file_path: str | Path) -> list[DocumentChunk]:
    """Load and validate chunks from a JSONL file."""
    path = Path(file_path)

    if not path.exists():
        return []

    chunks = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                chunks.append(DocumentChunk.model_validate(record))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid chunk record at line {line_number} "
                    f"in {path}"
                ) from exc

    return chunks
