
import json

from knowledge.ingestion.service import ingest_and_save
from knowledge.ingestion.storage import load_chunks, save_chunks


def test_ingest_and_save_document(tmp_path):
    source = tmp_path / "security.md"
    output = tmp_path / "processed" / "chunks.jsonl"
    source.write_text(
        "# Security\n\nUse strong authentication.",
        encoding="utf-8",
    )

    chunks = ingest_and_save(
        source,
        output,
        source_id="security-basics",
        title="Security Basics",
        publisher="CyberMind",
        license="Test",
        chunk_size=100,
        overlap=10,
    )

    loaded = load_chunks(output)
    assert len(chunks) == 1
    assert len(loaded) == 1
    assert loaded[0].chunk_id == "security-basics-0000"
    assert loaded[0].text == "# Security\n\nUse strong authentication."


def test_append_identical_document_skips_duplicate(tmp_path):
    source = tmp_path / "security.md"
    output = tmp_path / "chunks.jsonl"
    source.write_text("Same content.", encoding="utf-8")

    kwargs = {
        "source_id": "security",
        "title": "Security",
        "publisher": "CyberMind",
    }

    first = ingest_and_save(source, output, **kwargs)
    second = ingest_and_save(source, output, append=True, **kwargs)

    assert len(first) == 1
    assert second == []
    assert len(load_chunks(output)) == 1


def test_identical_content_refreshes_source_metadata_without_adding_chunks(
    tmp_path,
):
    source = tmp_path / "security.md"
    output = tmp_path / "chunks.jsonl"
    source.write_text("Same content.", encoding="utf-8")

    ingest_and_save(
        source,
        output,
        source_id="security",
        title="Old title",
        publisher="Old publisher",
    )
    result = ingest_and_save(
        source,
        output,
        source_id="security",
        title="Corrected title",
        publisher="Verified publisher",
    )

    loaded = load_chunks(output)
    assert result == []
    assert len(loaded) == 1
    assert loaded[0].metadata.title == "Corrected title"
    assert loaded[0].metadata.publisher == "Verified publisher"


def test_changed_document_replaces_old_chunks(tmp_path):
    source = tmp_path / "security.md"
    output = tmp_path / "chunks.jsonl"
    source.write_text("Original content.", encoding="utf-8")

    kwargs = {
        "source_id": "security",
        "title": "Security",
        "publisher": "CyberMind",
    }

    ingest_and_save(source, output, **kwargs)
    other_source = tmp_path / "other.md"
    other_source.write_text("Unrelated content.", encoding="utf-8")
    ingest_and_save(
        other_source,
        output,
        source_id="other",
        title="Other",
        publisher="CyberMind",
    )
    source.write_text("Updated content.", encoding="utf-8")

    updated = ingest_and_save(source, output, append=True, **kwargs)
    loaded = load_chunks(output)

    assert len(updated) == 1
    assert len(loaded) == 2
    assert next(chunk for chunk in loaded if chunk.source_id == "security").text == (
        "Updated content."
    )
    assert {chunk.source_id for chunk in loaded} == {"security", "other"}


def test_new_source_preserves_existing_source(tmp_path):
    source_a = tmp_path / "a.md"
    source_b = tmp_path / "b.md"
    output = tmp_path / "chunks.jsonl"
    source_a.write_text("Document A.", encoding="utf-8")
    source_b.write_text("Document B.", encoding="utf-8")

    ingest_and_save(
        source_a, output,
        source_id="source-a", title="A", publisher="CyberMind",
    )
    ingest_and_save(
        source_b, output,
        source_id="source-b", title="B", publisher="CyberMind",
        append=True,
    )

    loaded = load_chunks(output)
    assert {chunk.source_id for chunk in loaded} == {"source-a", "source-b"}


def test_default_ingestion_preserves_identical_content_from_other_source(
    tmp_path,
):
    source_a = tmp_path / "a.md"
    source_b = tmp_path / "b.md"
    output = tmp_path / "chunks.jsonl"
    source_a.write_text("Shared content.", encoding="utf-8")
    source_b.write_text("Shared content.", encoding="utf-8")

    ingest_and_save(
        source_a, output,
        source_id="source-a", title="A", publisher="Publisher A",
    )
    ingest_and_save(
        source_b, output,
        source_id="source-b", title="B", publisher="Publisher B",
    )

    loaded = load_chunks(output)
    assert {chunk.source_id for chunk in loaded} == {"source-a", "source-b"}
    assert {chunk.metadata.publisher for chunk in loaded} == {
        "Publisher A",
        "Publisher B",
    }


def test_duplicate_existing_records_are_cleaned(tmp_path):
    source = tmp_path / "security.md"
    output = tmp_path / "chunks.jsonl"
    source.write_text("Same content.", encoding="utf-8")

    kwargs = {
        "source_id": "security",
        "title": "Security",
        "publisher": "CyberMind",
    }

    chunks = ingest_and_save(source, output, **kwargs)
    unrelated = tmp_path / "unrelated.md"
    unrelated.write_text("Keep this source.", encoding="utf-8")
    ingest_and_save(
        unrelated,
        output,
        source_id="unrelated",
        title="Unrelated",
        publisher="CyberMind",
    )
    with output.open("a", encoding="utf-8") as file:
        for chunk in chunks:
            record = chunk.model_dump(mode="json")
            record["metadata"]["retrieved_at"] = "2020-01-01T00:00:00Z"
            file.write(json.dumps(record) + "\n")

    assert len(load_chunks(output)) == 3

    result = ingest_and_save(source, output, append=True, **kwargs)

    assert result == []
    loaded = load_chunks(output)
    assert len(loaded) == 2
    assert {chunk.source_id for chunk in loaded} == {"security", "unrelated"}
