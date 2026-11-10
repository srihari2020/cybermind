import io
import json
from urllib.error import HTTPError, URLError

import pytest

from knowledge.rag.providers import (
    LLMResponse,
    OllamaChatProvider,
    OllamaProviderError,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def make_result():
    return {
        "model": "qwen3.5:4b",
        "message": {
            "role": "assistant",
            "content": "Use parameterized queries.",
        },
        "total_duration": 5_000_000_000,
        "load_duration": 500_000_000,
        "prompt_eval_count": 20,
        "eval_count": 40,
        "eval_duration": 2_000_000_000,
    }


def test_provider_generates_response(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse(make_result())

    monkeypatch.setattr(
        "knowledge.rag.providers.urlopen",
        fake_urlopen,
    )

    provider = OllamaChatProvider()
    response = provider.generate("You are CyberMind.", "Prevent SQL injection.")

    assert isinstance(response, LLMResponse)
    assert response.content == "Use parameterized queries."
    assert response.model == "qwen3.5:4b"
    assert response.total_duration == 5.0
    assert response.load_duration == 0.5
    assert response.prompt_eval_count == 20
    assert response.eval_count == 40
    assert response.generation_duration == 2.0
    assert response.tokens_per_second == 20.0

    request_data = json.loads(captured["request"].data)

    assert request_data["model"] == "qwen3.5:4b"
    assert request_data["think"] is False
    assert request_data["stream"] is False
    assert request_data["keep_alive"] == "10m"
    assert request_data["messages"][0]["role"] == "system"
    assert request_data["messages"][1]["role"] == "user"
    assert captured["timeout"] == 120.0


def test_empty_user_prompt_is_rejected():
    provider = OllamaChatProvider()

    with pytest.raises(ValueError, match="cannot be empty"):
        provider.generate("System prompt", "  ")


def test_http_error_is_handled(monkeypatch):
    def fake_urlopen(request, timeout):
        raise HTTPError(
            request.full_url,
            404,
            "Not Found",
            None,
            io.BytesIO(b'{"error":"model not found"}'),
        )

    monkeypatch.setattr(
        "knowledge.rag.providers.urlopen",
        fake_urlopen,
    )

    provider = OllamaChatProvider()

    with pytest.raises(OllamaProviderError, match="HTTP 404"):
        provider.generate("System", "Question")


def test_connection_error_is_handled(monkeypatch):
    def fake_urlopen(request, timeout):
        raise URLError("Connection refused")

    monkeypatch.setattr(
        "knowledge.rag.providers.urlopen",
        fake_urlopen,
    )

    provider = OllamaChatProvider()

    with pytest.raises(OllamaProviderError, match="Cannot connect"):
        provider.generate("System", "Question")


def test_empty_model_response_is_rejected(monkeypatch):
    result = make_result()
    result["message"]["content"] = "   "

    monkeypatch.setattr(
        "knowledge.rag.providers.urlopen",
        lambda request, timeout: FakeResponse(result),
    )

    provider = OllamaChatProvider()

    with pytest.raises(OllamaProviderError, match="empty response"):
        provider.generate("System", "Question")


def test_invalid_json_is_handled(monkeypatch):
    class InvalidResponse(FakeResponse):
        def __init__(self):
            self.payload = b"not valid json"

    monkeypatch.setattr(
        "knowledge.rag.providers.urlopen",
        lambda request, timeout: InvalidResponse(),
    )

    provider = OllamaChatProvider()

    with pytest.raises(OllamaProviderError, match="invalid JSON"):
        provider.generate("System", "Question")


def test_invalid_configuration_is_rejected():
    with pytest.raises(ValueError):
        OllamaChatProvider(timeout=0)

    with pytest.raises(ValueError):
        OllamaChatProvider(num_ctx=0)

    with pytest.raises(ValueError):
        OllamaChatProvider(num_predict=0)
