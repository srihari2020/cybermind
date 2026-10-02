import pytest

from knowledge.ingestion.cli import main
from knowledge.ingestion.storage import load_chunks


def test_cli_single_file_ingestion_and_repeat_skip(tmp_path, monkeypatch, capsys):
    source = tmp_path / "security.md"
    output = tmp_path / "store" / "knowledge.jsonl"
    source.write_text("Local security notes.", encoding="utf-8")
    arguments = [
        str(source),
        "--source-id",
        "local-security",
        "--title",
        "Local Security",
        "--publisher",
        "CyberMind test",
        "--output",
        str(output),
    ]

    monkeypatch.setattr("sys.argv", ["cybermind-ingest", *arguments])
    assert main() == 0
    first_output = capsys.readouterr().out
    assert "Ingested:" in first_output
    assert len(load_chunks(output)) == 1

    monkeypatch.setattr("sys.argv", ["cybermind-ingest", *arguments])
    assert main() == 0
    second_output = capsys.readouterr().out
    assert "Skipped duplicate:" in second_output
    assert "Skipped duplicates: 1" in second_output
    assert len(load_chunks(output)) == 1


def test_cli_nested_directory_uses_relative_paths_and_continues_failures(
    tmp_path, monkeypatch, capsys, caplog
):
    root = tmp_path / "documents"
    output = tmp_path / "knowledge.jsonl"
    (root / "one").mkdir(parents=True)
    (root / "two").mkdir()
    (root / "one" / "guide.md").write_text("One guide.", encoding="utf-8")
    (root / "two" / "guide.md").write_text("Two guide.", encoding="utf-8")
    (root / "bad.txt").write_bytes(b"\xff invalid utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "cybermind-ingest",
            str(root),
            "--publisher",
            "CyberMind test",
            "--output",
            str(output),
        ],
    )

    assert main() == 1
    captured = capsys.readouterr()
    records = load_chunks(output)
    assert len(records) == 2
    assert {chunk.source_id for chunk in records} == {
        "batch:documents/one/guide.md",
        "batch:documents/two/guide.md",
    }
    assert "Successful files: 2" in captured.out
    assert "Failed files: 1" in captured.out
    assert "Failed to process" in caplog.text

    assert main() == 1
    repeated_output = capsys.readouterr().out
    assert "Skipped duplicates: 2" in repeated_output
    assert "Chunks generated: 0" in repeated_output
    assert len(load_chunks(output)) == 2


@pytest.mark.parametrize(
    "options, message",
    [
        (["--chunk-size", "0"], "--chunk-size must be greater than zero"),
        (["--chunk-size", "10", "--overlap", "10"], "--overlap must be"),
    ],
)
def test_cli_rejects_invalid_chunk_options(
    tmp_path, monkeypatch, capsys, options, message
):
    source = tmp_path / "valid.txt"
    source.write_text("valid", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "cybermind-ingest",
            str(source),
            "--source-id",
            "source",
            "--title",
            "Valid",
            "--publisher",
            "CyberMind test",
            *options,
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2
    assert message in capsys.readouterr().err


def test_cli_requires_source_and_title_for_single_file(tmp_path, monkeypatch, capsys):
    source = tmp_path / "valid.md"
    output = tmp_path / "knowledge.jsonl"
    source.write_text("Valid content.", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "cybermind-ingest",
            str(source),
            "--publisher",
            "CyberMind test",
            "--output",
            str(output),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    assert "--source-id and --title are required" in capsys.readouterr().err
    assert not output.exists()


def test_cli_rejects_output_that_would_overwrite_input(
    tmp_path, monkeypatch, capsys
):
    source = tmp_path / "source.md"
    original = "Keep the source document."
    source.write_text(original, encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "cybermind-ingest",
            str(source),
            "--source-id",
            "source",
            "--title",
            "Source",
            "--publisher",
            "CyberMind test",
            "--output",
            str(source),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    assert "must not overwrite an input document" in capsys.readouterr().err
    assert source.read_text(encoding="utf-8") == original