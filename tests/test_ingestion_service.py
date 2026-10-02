
from knowledge.ingestion.service import ingest_and_save
from knowledge.ingestion.storage import load_chunks


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


def test_ingest_and_save_multiple_documents(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    output = tmp_path / "chunks.jsonl"

    first.write_text("First document.", encoding="utf-8")
    second.write_text("Second document.", encoding="utf-8")

    ingest_and_save(
        first,
        output,
        source_id="first",
        title="First",
        publisher="CyberMind",
    )

    ingest_and_save(
        second,
        output,
        source_id="second",
        title="Second",
        publisher="CyberMind",
        append=True,
    )

    loaded = load_chunks(output)

    assert len(loaded) == 2
    assert loaded[0].source_id == "first"
    assert loaded[1].source_id == "second"
