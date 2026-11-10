from knowledge.rag.citations import validate_citations
from knowledge.rag.context import ContextBundle, Evidence


def make_context():
    return ContextBundle(
        evidence=(
            Evidence(
                citation_id="S1",
                source_id="source-1",
                chunk_id="chunk-1",
                title="SQL Security",
                publisher="CyberMind Test",
                similarity=0.85,
                text="Use parameterized queries.",
            ),
            Evidence(
                citation_id="S2",
                source_id="source-2",
                chunk_id="chunk-2",
                title="Database Security",
                publisher="CyberMind Test",
                similarity=0.75,
                text="Apply least privilege.",
            ),
        )
    )


def test_valid_citations():
    result = validate_citations(
        "Use parameterized queries [S1].",
        make_context(),
    )

    assert result.is_valid
    assert result.cited_ids == ("S1",)
    assert result.unknown_ids == ()


def test_multiple_citations():
    result = validate_citations(
        "Use parameterized queries [S1]. Apply least privilege [S2].",
        make_context(),
    )

    assert result.is_valid
    assert result.cited_ids == ("S1", "S2")


def test_duplicate_citations_are_deduplicated():
    result = validate_citations(
        "Evidence [S1] confirms this. See also [S1].",
        make_context(),
    )

    assert result.cited_ids == ("S1",)
    assert result.is_valid


def test_unknown_citation_is_rejected():
    result = validate_citations(
        "This is supported by [S9].",
        make_context(),
    )

    assert not result.is_valid
    assert result.unknown_ids == ("S9",)


def test_missing_citation_is_detected():
    result = validate_citations(
        "Parameterized queries prevent SQL injection.",
        make_context(),
    )

    assert not result.is_valid
    assert result.missing_required


def test_empty_context_does_not_require_citations():
    result = validate_citations(
        "There is insufficient evidence.",
        ContextBundle(evidence=()),
    )

    assert result.is_valid
    assert not result.missing_required
