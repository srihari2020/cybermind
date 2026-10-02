
import pytest

from knowledge.ingestion.pipeline import (
    calculate_sha256,
    normalize_text,
    split_into_chunks,
    ingest_file,
)


def test_normalize_text():
    result = normalize_text(
        "  Hello   world \r\n\r\n\r\n Next line  "
    )
    assert result == "Hello world\n\nNext line"


def test_split_into_chunks():
    text = "word " * 300

    chunks = split_into_chunks(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)
    assert all(chunks)


def test_split_into_chunks_preserves_overlap_without_tiny_boundary_chunks():
    chunks = split_into_chunks(
        "abcdefghij klmnopqrst uvwxyz",
        chunk_size=10,
        overlap=3,
    )

    assert len(chunks) > 1
    assert all(len(chunk) <= 10 for chunk in chunks)
    assert all(len(chunk) > 3 for chunk in chunks[:-1])
    assert any(left[-3:] == right[:3] for left, right in zip(chunks, chunks[1:]))


def test_split_empty_text():
    assert split_into_chunks("   ") == []


def test_invalid_chunk_settings():
    with pytest.raises(ValueError):
        split_into_chunks("some text", chunk_size=0)

    with pytest.raises(ValueError):
        split_into_chunks(
            "some text",
            chunk_size=100,
            overlap=100,
        )


def test_calculate_sha256():
    first = calculate_sha256(b"CyberMind")
    second = calculate_sha256(b"CyberMind")
    different = calculate_sha256(b"cybermind")

    assert first == second
    assert first != different


def test_ingest_file(tmp_path):
    document = tmp_path / "security.md"
    document.write_text(
        "# Security\n\nUse strong authentication.",
        encoding="utf-8",
    )

    chunks = ingest_file(
        document,
        source_id="test-security",
        title="Security Basics",
        publisher="CyberMind Test",
        license="Test",
        chunk_size=100,
        overlap=10,
    )

    assert len(chunks) == 1
    assert chunks[0].source_id == "test-security"
    assert chunks[0].chunk_index == 0
    assert chunks[0].metadata.title == "Security Basics"
    assert chunks[0].metadata.sha256


def test_ingest_rejects_unsupported_file(tmp_path):
    document = tmp_path / "security.pdf"
    document.write_text(
        "Not supported yet",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported file type"):
        ingest_file(
            document,
            source_id="test-pdf",
            title="Test PDF",
            publisher="CyberMind Test",
        )


def test_ingest_rejects_empty_file(tmp_path):
    document = tmp_path / "empty.txt"
    document.write_text(" \n\t", encoding="utf-8")

    with pytest.raises(ValueError, match="Document is empty"):
        ingest_file(
            document,
            source_id="empty",
            title="Empty",
            publisher="CyberMind Test",
        )
