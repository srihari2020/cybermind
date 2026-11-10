from types import SimpleNamespace

from knowledge.rag.context import build_context


def make_result(
    source_id="source-1",
    chunk_id="chunk-1",
    title="Web Security",
    publisher="CyberMind",
    similarity=0.85,
    text="Use parameterized queries.",
):
    metadata = SimpleNamespace(
        title=title,
        publisher=publisher,
    )

    chunk = SimpleNamespace(
        metadata=metadata,
        text=text,
    )

    return SimpleNamespace(
        chunk=chunk,
        source_id=source_id,
        chunk_id=chunk_id,
        title=title,
        publisher=publisher,
        similarity=similarity,
    )


def test_build_context_assigns_citation_ids():
    results = [
        make_result(),
        make_result(
            source_id="source-2",
            chunk_id="chunk-2",
            title="Network Security",
            text="Use firewalls.",
        ),
    ]

    context = build_context(results)

    assert len(context.evidence) == 2
    assert context.evidence[0].citation_id == "S1"
    assert context.evidence[1].citation_id == "S2"


def test_build_context_preserves_source_metadata():
    result = make_result()
    context = build_context([result])

    evidence = context.evidence[0]

    assert evidence.source_id == "source-1"
    assert evidence.chunk_id == "chunk-1"
    assert evidence.title == "Web Security"
    assert evidence.publisher == "CyberMind"
    assert evidence.similarity == 0.85
    assert evidence.text == "Use parameterized queries."


def test_render_context_contains_evidence():
    context = build_context([make_result()])

    rendered = context.render()

    assert "[S1]" in rendered
    assert "Web Security" in rendered
    assert "CyberMind" in rendered
    assert "Use parameterized queries." in rendered
    assert "0.8500" in rendered


def test_empty_context():
    context = build_context([])

    assert context.is_empty
    assert context.render() == ""
    assert context.evidence == ()
