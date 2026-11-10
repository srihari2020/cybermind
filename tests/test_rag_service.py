from types import SimpleNamespace

import pytest

from knowledge.rag.providers import LLMResponse, OllamaProviderError
from knowledge.rag.service import (
    INSUFFICIENT_EVIDENCE,
    INVALID_CITATION_RESPONSE,
    RAGService,
)


def make_result():
    return SimpleNamespace(
        source_id="sql-security",
        chunk_id="chunk-1",
        title="SQL Security Guide",
        publisher="CyberMind Test",
        similarity=0.90,
        chunk=SimpleNamespace(
            text="Use parameterized queries to prevent SQL injection."
        ),
    )


def make_response(content):
    return LLMResponse(
        content=content,
        model="qwen3.5:4b",
        total_duration=2.0,
        load_duration=0.1,
        prompt_eval_count=50,
        eval_count=40,
        generation_duration=1.0,
    )


class FakeRetrieval:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def search(self, query, top_k=5, min_similarity=None):
        self.calls.append((query, top_k, min_similarity))
        return self.results


class FakeProvider:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def generate(self, system_prompt, user_prompt):
        self.calls.append((system_prompt, user_prompt))
        return self.response


def test_successful_rag_answer():
    retrieval = FakeRetrieval([make_result()])
    provider = FakeProvider(
        make_response(
            "Use parameterized queries to prevent SQL injection [S1]."
        )
    )

    service = RAGService(retrieval, provider)
    result = service.answer("  How do I prevent SQL injection?  ")

    assert result.question == "How do I prevent SQL injection?"
    assert "parameterized queries" in result.answer
    assert not result.abstained
    assert result.citations_valid
    assert result.citation_validation.cited_ids == ("S1",)
    assert len(result.evidence) == 1
    assert result.model == "qwen3.5:4b"
    assert result.total_duration == 2.0
    assert result.tokens_per_second == 40.0

    assert retrieval.calls == [
        ("How do I prevent SQL injection?", 5, None)
    ]
    assert len(provider.calls) == 1


def test_empty_evidence_causes_abstention():
    retrieval = FakeRetrieval([])
    provider = FakeProvider(None)

    service = RAGService(retrieval, provider)
    result = service.answer("How do I detect malware?")

    assert result.abstained
    assert result.answer == INSUFFICIENT_EVIDENCE
    assert result.evidence == ()
    assert result.model is None
    assert provider.calls == []


def test_unknown_citation_causes_abstention():
    retrieval = FakeRetrieval([make_result()])
    provider = FakeProvider(
        make_response("This is supported by an unknown source [S9].")
    )

    service = RAGService(retrieval, provider)
    result = service.answer("How do I prevent SQL injection?")

    assert result.abstained
    assert result.answer == INVALID_CITATION_RESPONSE
    assert result.citation_validation.unknown_ids == ("S9",)
    assert result.draft_answer is not None


def test_missing_citation_causes_abstention():
    retrieval = FakeRetrieval([make_result()])
    provider = FakeProvider(
        make_response("Use parameterized queries to prevent SQL injection.")
    )

    service = RAGService(retrieval, provider)
    result = service.answer("How do I prevent SQL injection?")

    assert result.abstained
    assert result.citation_validation.missing_required
    assert result.answer == INVALID_CITATION_RESPONSE


def test_empty_question_is_rejected():
    service = RAGService(
        FakeRetrieval([]),
        FakeProvider(None),
    )

    with pytest.raises(ValueError, match="Question cannot be empty"):
        service.answer("   ")


def test_retrieval_configuration_is_respected():
    retrieval = FakeRetrieval([make_result()])
    provider = FakeProvider(
        make_response("Use parameterized queries [S1].")
    )

    service = RAGService(
        retrieval,
        provider,
        top_k=3,
        min_similarity=0.6,
    )

    service.answer("Prevent SQL injection")

    assert retrieval.calls == [
        ("Prevent SQL injection", 3, 0.6)
    ]


def test_provider_error_propagates():
    retrieval = FakeRetrieval([make_result()])

    class FailingProvider:
        def generate(self, system_prompt, user_prompt):
            raise OllamaProviderError("Ollama unavailable")

    service = RAGService(retrieval, FailingProvider())

    with pytest.raises(OllamaProviderError, match="Ollama unavailable"):
        service.answer("Prevent SQL injection")


def test_invalid_top_k_is_rejected():
    with pytest.raises(ValueError, match="top_k"):
        RAGService(
            FakeRetrieval([]),
            FakeProvider(None),
            top_k=0,
        )
