
import json

import pytest

from knowledge.ingestion.models import DocumentChunk, DocumentMetadata
from knowledge.ingestion.storage import load_chunks, save_chunks


@pytest.fixture
def sample_chunks():
    metadata = DocumentMetadata(
        source_id="test-source",
        title="Cybersecurity Basics",
        publisher="CyberMind Tests",
        license="Test",
        sha256="a" * 64,
    )

    return [
        DocumentChunk(
            chunk_id="test-source-0000",
            source_id="test-source",
            chunk_index=0,
            text="Use strong authentication.",
            metadata=metadata,
        ),
        DocumentChunk(
            chunk_id="test-source-0001",
            source_id="test-source",
            chunk_index=1,
            text="Keep systems updated.",
            metadata=metadata,
        ),
    ]


def test_save_and_load_chunks(tmp_path, sample_chunks):
    file_path = tmp_path / "chunks.jsonl"

    saved_count = save_chunks(sample_chunks, file_path)
    loaded_chunks = load_chunks(file_path)

    assert saved_count == 2
    assert len(loaded_chunks) == 2
    assert loaded_chunks[0].text == "Use strong authentication."
    assert loaded_chunks[1].chunk_index == 1
    assert loaded_chunks[0].metadata.title == "Cybersecurity Basics"


def test_save_empty_chunks_creates_file(tmp_path):
    file_path = tmp_path / "empty.jsonl"

    saved_count = save_chunks([], file_path)

    assert saved_count == 0
    assert file_path.exists()
    assert load_chunks(file_path) == []


def test_load_missing_file(tmp_path):
    file_path = tmp_path / "missing.jsonl"

    assert load_chunks(file_path) == []


def test_append_chunks(tmp_path, sample_chunks):
    file_path = tmp_path / "chunks.jsonl"

    save_chunks(sample_chunks[:1], file_path)
    save_chunks(sample_chunks[1:], file_path, append=True)

    loaded_chunks = load_chunks(file_path)

    assert len(loaded_chunks) == 2
    assert loaded_chunks[0].chunk_index == 0
    assert loaded_chunks[1].chunk_index == 1


def test_invalid_jsonl_record(tmp_path):
    file_path = tmp_path / "invalid.jsonl"
    file_path.write_text("{invalid json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="line 1"):
        load_chunks(file_path)


def test_blank_lines_are_ignored(tmp_path, sample_chunks):
    file_path = tmp_path / "chunks.jsonl"

    save_chunks(sample_chunks[:1], file_path)
    with file_path.open("a", encoding="utf-8") as file:
        file.write("\n")

    loaded_chunks = load_chunks(file_path)

    assert len(loaded_chunks) == 1
