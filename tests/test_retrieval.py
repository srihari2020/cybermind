import json
import math

import pytest

from knowledge.ingestion.models import DocumentChunk, DocumentMetadata
from knowledge.ingestion.service import ingest_and_save
from knowledge.ingestion.storage import save_chunks
from knowledge.retrieval.embeddings import SentenceTransformerEmbeddings
from knowledge.retrieval.index import PersistentVectorIndex, VectorEntry
from knowledge.retrieval.service import SemanticRetrievalService


class FakeModel:
    def __init__(self):
        self.calls = 0

    def get_sentence_embedding_dimension(self):
        return 3

    def encode(self, texts, **kwargs):
        self.calls += 1
        vectors = []
        for text in texts:
            lowered = text.lower()
            if "authentication" in lowered or "account" in lowered:
                vectors.append([3.0, 0.0, 0.0])
            elif "network" in lowered or "firewall" in lowered:
                vectors.append([0.0, 2.0, 0.0])
            else:
                vectors.append([0.0, 0.0, 4.0])
        return vectors


class FakeEmbeddings:
    model_name = "test/fake-3d"
    dimension = 3

    def __init__(self):
        self.calls = []

    def _vector(self, text):
        lowered = text.lower()
        if "authentication" in lowered or "account" in lowered:
            return [1.0, 0.0, 0.0]
        if "network" in lowered or "firewall" in lowered:
            return [0.0, 1.0, 0.0]
        return [0.0, 0.0, 1.0]

    def embed_texts(self, texts):
        self.calls.append(list(texts))
        return [self._vector(text) for text in texts]

    def embed_chunks(self, chunks):
        return self.embed_texts([chunk.text for chunk in chunks])

    def embed_query(self, query):
        return self.embed_texts([query])[0]


@pytest.fixture
def chunks():
    records = []
    for chunk_id, text, publisher in [
        ("auth-0000", "Multi-factor authentication protects accounts.", "Org A"),
        ("network-0000", "A firewall filters network traffic.", "Org B"),
        ("policy-0000", "Security policies define responsibilities.", "Org C"),
    ]:
        source_id = chunk_id.split("-")[0]
        metadata = DocumentMetadata(
            source_id=source_id,
            title=f"{source_id.title()} Guide",
            publisher=publisher,
            sha256="a" * 64,
        )
        records.append(
            DocumentChunk(
                chunk_id=chunk_id,
                source_id=source_id,
                chunk_index=0,
                text=text,
                metadata=metadata,
            )
        )
    return records


def test_embedding_is_lazy_normalized_and_reused():
    model = FakeModel()
    embedder = SentenceTransformerEmbeddings(
        "test/model",
        model_loader=lambda name: model,
    )

    assert model.calls == 0
    assert embedder.embed_texts([]) == []
    assert model.calls == 0
    vectors = embedder.embed_texts(["authentication", "network firewall"])

    assert model.calls == 1
    assert embedder.dimension == 3
    assert [len(vector) for vector in vectors] == [3, 3]
    assert all(math.isclose(sum(value**2 for value in vector), 1.0) for vector in vectors)
    embedder.embed_query("account security")
    assert model.calls == 2


def test_embedding_handles_chunks_and_rejects_empty_query(chunks):
    model = FakeModel()
    embedder = SentenceTransformerEmbeddings("test/model", model_loader=lambda _: model)

    assert len(embedder.embed_chunks(chunks[:2])) == 2
    with pytest.raises(ValueError, match="Query must not be empty"):
        embedder.embed_query("  ")


def test_embedding_load_failures_are_actionable():
    embedder = SentenceTransformerEmbeddings(
        "missing/model",
        model_loader=lambda _: (_ for _ in ()).throw(OSError("offline")),
    )
    with pytest.raises(RuntimeError, match="Could not load embedding model"):
        embedder.embed_query("account security")


def test_missing_embedding_dependency_is_actionable(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    embedder = SentenceTransformerEmbeddings()

    with pytest.raises(RuntimeError, match="requires sentence-transformers"):
        embedder.embed_query("account security")


def test_index_persists_reloads_and_deduplicates(tmp_path):
    path = tmp_path / "vectors.json"
    entry = VectorEntry("auth", "auth-0", "Auth", "Org", "hash", (1, 0, 0))
    index = PersistentVectorIndex(path)
    index.replace([entry, entry], model_name="test/model", dimension=3)

    loaded = PersistentVectorIndex(path, model_name="test/model")
    assert len(loaded.entries) == 1
    assert loaded.entries[0].vector == (1.0, 0.0, 0.0)
    assert json.loads(path.read_text(encoding="utf-8"))["metric"] == "cosine"


def test_failed_index_write_preserves_file_and_in_memory_state(
    tmp_path, monkeypatch
):
    path = tmp_path / "vectors.json"
    index = PersistentVectorIndex(path)
    original = VectorEntry("auth", "auth-0", "Auth", "Org", "hash", (1, 0, 0))
    index.replace([original], model_name="test/model", dimension=3)
    original_file = path.read_bytes()

    def fail_replace(source, destination):
        raise OSError("simulated replace failure")

    monkeypatch.setattr("knowledge.retrieval.index.os.replace", fail_replace)
    replacement = VectorEntry("network", "network-0", "Network", "Org", "hash2", (0, 1, 0))
    with pytest.raises(OSError, match="simulated replace failure"):
        index.replace([replacement], model_name="test/model", dimension=3)

    assert path.read_bytes() == original_file
    assert index.entries == (original,)


def test_index_similarity_order_top_k_and_threshold(tmp_path):
    index = PersistentVectorIndex(tmp_path / "vectors.json")
    entries = [
        VectorEntry("auth", "a", "A", "Org", "1", (1, 0, 0)),
        VectorEntry("network", "n", "N", "Org", "2", (0.8, 0.6, 0)),
        VectorEntry("policy", "p", "P", "Org", "3", (0, 1, 0)),
    ]
    index.replace(entries, model_name="test/model", dimension=3)

    assert [match.chunk_id for match in index.search((1, 0, 0), top_k=2)] == ["a", "n"]
    assert [match.chunk_id for match in index.search(
        (1, 0, 0), min_similarity=0.9
    )] == ["a"]
    assert index.search((1, 0, 0))[0].similarity == pytest.approx(1.0)


def test_index_detects_model_and_dimension_mismatch(tmp_path):
    path = tmp_path / "vectors.json"
    index = PersistentVectorIndex(path)
    index.replace(
        [VectorEntry("a", "a", "A", "Org", "h", (1, 0, 0))],
        model_name="test/model",
        dimension=3,
    )
    with pytest.raises(ValueError, match="Rebuild the index"):
        PersistentVectorIndex(path, model_name="other/model")
    with pytest.raises(ValueError, match="dimension is 3"):
        index.replace([], model_name="test/model", dimension=2)
    with pytest.raises(ValueError, match="Query vector dimension"):
        index.search((1, 0), top_k=1)


def test_empty_index_and_stale_chunk_ids_are_safe(tmp_path, chunks):
    store = tmp_path / "knowledge.jsonl"
    index_path = tmp_path / "vectors.json"
    save_chunks(chunks, store)
    embeddings = FakeEmbeddings()
    service = SemanticRetrievalService(store, index_path, embeddings=embeddings)

    assert service.search("account authentication") == []
    service.index.replace(
        [VectorEntry("missing", "gone", "Gone", "Org", "h", (1, 0, 0))],
        model_name=embeddings.model_name,
        dimension=3,
    )
    assert service.search("account authentication") == []


def test_rebuild_search_metadata_threshold_and_incremental_index(tmp_path, chunks):
    store = tmp_path / "knowledge.jsonl"
    index_path = tmp_path / "vectors.json"
    save_chunks(chunks, store)
    embeddings = FakeEmbeddings()
    service = SemanticRetrievalService(store, index_path, embeddings=embeddings)

    first = service.index_chunks()
    assert first.indexed == 3
    assert first.reused == 0
    assert len(embeddings.calls[0]) == 3

    second = service.index_chunks()
    assert second.indexed == 0
    assert second.reused == 3
    assert len(embeddings.calls) == 1

    results = service.search("How does authentication protect accounts?", top_k=2)
    assert [result.source_id for result in results] == ["auth", "network"]
    assert results[0].title == "Auth Guide"
    assert results[0].publisher == "Org A"
    assert results[0].chunk_id == "auth-0000"
    assert results[0].similarity == pytest.approx(1.0)
    with pytest.raises(ValueError, match="between -1 and 1"):
        service.search("account authentication", min_similarity=1.01)


def test_service_applies_similarity_threshold_and_syncs_removed_chunks(
    tmp_path, chunks
):
    store = tmp_path / "knowledge.jsonl"
    index_path = tmp_path / "vectors.json"
    save_chunks(chunks, store)
    service = SemanticRetrievalService(store, index_path, embeddings=FakeEmbeddings())
    service.index_chunks()

    assert service.search("account authentication", min_similarity=1.0)[0].source_id == "auth"
    with pytest.raises(ValueError, match="between -1 and 1"):
        service.search("account authentication", min_similarity=1.1)

    save_chunks(chunks[:1], store)
    summary = service.index_chunks()
    assert summary.removed == 2
    assert len(service.index.entries) == 1


def test_rebuild_can_change_models_and_replaces_all_vectors(tmp_path, chunks):
    store = tmp_path / "knowledge.jsonl"
    index_path = tmp_path / "vectors.json"
    save_chunks(chunks, store)
    first_service = SemanticRetrievalService(
        store,
        index_path,
        embeddings=FakeEmbeddings(),
    )
    first_service.index_chunks()

    replacement_embeddings = FakeEmbeddings()
    replacement_embeddings.model_name = "test/replacement"
    replacement_service = SemanticRetrievalService(
        store,
        index_path,
        embeddings=replacement_embeddings,
    )
    with pytest.raises(ValueError, match="Rebuild the index"):
        replacement_service.index_chunks()

    rebuilt = replacement_service.index_chunks(rebuild=True)
    assert rebuilt.indexed == 3
    assert rebuilt.reused == 0
    assert PersistentVectorIndex(index_path).model_name == "test/replacement"


def test_cli_index_and_search_with_injected_fake_embeddings(
    tmp_path, monkeypatch, capsys
):
    from knowledge.retrieval import cli

    store = tmp_path / "knowledge.jsonl"
    index = tmp_path / "knowledge.index.json"
    document = tmp_path / "security.md"
    document.write_text(
        "Multi-factor authentication protects accounts.",
        encoding="utf-8",
    )
    ingest_and_save(
        document,
        store,
        source_id="auth",
        title="Auth Guide",
        publisher="Org A",
    )
    monkeypatch.setattr(cli, "SentenceTransformerEmbeddings", lambda name: FakeEmbeddings())
    monkeypatch.setattr(
        "sys.argv",
        [
            "cybermind-retrieval",
            "index",
            "--store",
            str(store),
            "--index",
            str(index),
        ],
    )

    assert cli.main() == 0
    assert "Indexed 1 chunks" in capsys.readouterr().out

    monkeypatch.setattr(
        "sys.argv",
        [
            "cybermind-retrieval",
            "search",
            "account authentication",
            "--store",
            str(store),
            "--index",
            str(index),
            "--top-k",
            "1",
            "--min-similarity",
            "0.9",
        ],
    )
    assert cli.main() == 0
    output = capsys.readouterr().out
    assert "similarity=1.0000" in output
    assert "source_id=auth" in output
    assert "Title: Auth Guide" in output
    assert "Publisher: Org A" in output
    assert "Multi-factor authentication protects accounts." in output


def test_cli_rejects_invalid_top_k(tmp_path, monkeypatch, capsys):
    from knowledge.retrieval.cli import main

    store = tmp_path / "knowledge.jsonl"
    store.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "cybermind-retrieval",
            "search",
            "authentication",
            "--store",
            str(store),
            "--top-k",
            "0",
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2
    assert "--top-k must be greater than zero" in capsys.readouterr().err
