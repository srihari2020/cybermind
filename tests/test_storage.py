
import json

import pytest

from knowledge.ingestion.models import DocumentChunk, DocumentMetadata
import knowledge.ingestion.storage as storage
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


def test_append_skips_existing_chunk_ids_and_returns_new_count(
    tmp_path, sample_chunks
):
    file_path = tmp_path / "chunks.jsonl"
    save_chunks(sample_chunks[:1], file_path)

    assert save_chunks(sample_chunks, file_path, append=True) == 1
    assert save_chunks(sample_chunks, file_path, append=True) == 0
    assert len(load_chunks(file_path)) == 2


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


def test_malformed_record_reports_line_number(tmp_path, sample_chunks):
    file_path = tmp_path / "malformed.jsonl"
    file_path.write_text(
        json.dumps(sample_chunks[0].model_dump(mode="json")) + "\n{}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="line 2"):
        load_chunks(file_path)


def test_invalid_utf8_reports_line_number(tmp_path, sample_chunks):
    file_path = tmp_path / "invalid-encoding.jsonl"
    first_line = json.dumps(sample_chunks[0].model_dump(mode="json")).encode()
    file_path.write_bytes(first_line + b"\n\xff\n")

    with pytest.raises(ValueError, match="line 2"):
        load_chunks(file_path)


def test_chunk_and_metadata_source_ids_must_match(tmp_path, sample_chunks):
    file_path = tmp_path / "wrong-source.jsonl"
    record = sample_chunks[0].model_dump(mode="json")
    record["metadata"]["source_id"] = "another-source"
    file_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="source_id values do not match"):
        load_chunks(file_path)


def test_duplicate_chunk_ids_are_deduplicated_on_save(tmp_path, sample_chunks):
    file_path = tmp_path / "duplicates.jsonl"

    assert save_chunks(sample_chunks + [sample_chunks[0]], file_path) == 2
    assert len(load_chunks(file_path)) == 2


def test_conflicting_chunk_id_does_not_replace_existing_file(
    tmp_path, sample_chunks
):
    file_path = tmp_path / "chunks.jsonl"
    save_chunks(sample_chunks[:1], file_path)
    original = file_path.read_bytes()
    conflicting = sample_chunks[0].model_copy(update={"text": "Conflicting"})

    with pytest.raises(ValueError, match="Conflicting records"):
        save_chunks([conflicting], file_path, append=True)

    assert file_path.read_bytes() == original


def test_failed_atomic_replace_preserves_existing_file(
    tmp_path, sample_chunks, monkeypatch
):
    file_path = tmp_path / "chunks.jsonl"
    save_chunks(sample_chunks[:1], file_path)
    original = file_path.read_bytes()

    def fail_replace(source, destination):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(storage.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated replace failure"):
        save_chunks(sample_chunks[1:], file_path)

    assert file_path.read_bytes() == original
    assert list(tmp_path.glob("*.tmp")) == []
