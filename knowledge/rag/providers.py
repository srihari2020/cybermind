from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaProviderError(RuntimeError):
    """Raised when the Ollama provider cannot generate a response."""


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str
    total_duration: float
    load_duration: float
    prompt_eval_count: int
    eval_count: int
    generation_duration: float

    @property
    def tokens_per_second(self) -> float:
        if self.generation_duration <= 0:
            return 0.0

        return self.eval_count / self.generation_duration


class OllamaChatProvider:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
        keep_alive: str = "10m",
        num_ctx: int = 2048,
        num_predict: int = 512,
        temperature: float = 0.2,
        think: bool = False,
    ) -> None:
        self.base_url = (
            base_url or os.getenv(
                "CYBERMIND_OLLAMA_URL",
                "http://127.0.0.1:11434",
            )
        ).rstrip("/")

        self.model = model or os.getenv(
            "CYBERMIND_LLM_MODEL",
            "qwen3.5:4b",
        )

        if not self.model.strip():
            raise ValueError("Model name cannot be empty")

        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero")

        if num_ctx <= 0 or num_predict <= 0:
            raise ValueError("Context and prediction limits must be positive")

        self.timeout = timeout
        self.keep_alive = keep_alive
        self.num_ctx = num_ctx
        self.num_predict = num_predict
        self.temperature = temperature
        self.think = think

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:
        if not user_prompt.strip():
            raise ValueError("User prompt cannot be empty")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "think": self.think,
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {
                "num_ctx": self.num_ctx,
                "num_predict": self.num_predict,
                "temperature": self.temperature,
            },
        }

        request = Request(
            url=f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OllamaProviderError(
                f"Ollama returned HTTP {exc.code}: {detail}"
            ) from exc

        except (URLError, TimeoutError, OSError) as exc:
            raise OllamaProviderError(
                f"Cannot connect to Ollama at {self.base_url}: {exc}"
            ) from exc

        except json.JSONDecodeError as exc:
            raise OllamaProviderError(
                "Ollama returned invalid JSON"
            ) from exc

        if result.get("error"):
            raise OllamaProviderError(result["error"])

        message = result.get("message") or {}
        content = message.get("content", "").strip()

        if not content:
            raise OllamaProviderError(
                "Ollama returned an empty response"
            )

        generation_duration = (
            result.get("eval_duration", 0) / 1_000_000_000
        )

        return LLMResponse(
            content=content,
            model=result.get("model", self.model),
            total_duration=result.get("total_duration", 0) / 1_000_000_000,
            load_duration=result.get("load_duration", 0) / 1_000_000_000,
            prompt_eval_count=result.get("prompt_eval_count", 0),
            eval_count=result.get("eval_count", 0),
            generation_duration=generation_duration,
        )
