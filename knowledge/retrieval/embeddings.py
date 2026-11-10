import logging
import os
from collections.abc import Sequence
from typing import Any

from knowledge.ingestion.models import DocumentChunk
from knowledge.retrieval.vectors import normalize_vector


DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddings:
    """Lazily load and reuse a SentenceTransformer embedding model."""

    def __init__(
        self,
        model_name: str | None = None,
        *,
        model_loader=None,
    ) -> None:
        self.model_name = (
            model_name
            or os.environ.get("CYBERMIND_EMBEDDING_MODEL")
            or DEFAULT_MODEL_NAME
        )
        self._model_loader = model_loader
        self._model: Any | None = None
        self._dimension: int | None = None
        self.device: str | None = None

    def _resolve_device(self) -> str:
        requested = os.environ.get(
            "CYBERMIND_EMBEDDING_DEVICE", "auto"
        ).strip().lower()

        if requested not in {"auto", "cuda", "cpu"}:
            raise ValueError(
                "CYBERMIND_EMBEDDING_DEVICE must be auto, cuda, or cpu"
            )

        if requested == "cpu":
            return "cpu"

        try:
            import torch
        except ImportError as exc:
            if requested == "cuda":
                raise RuntimeError(
                    "CUDA was requested, but PyTorch is not installed."
                ) from exc
            return "cpu"

        if requested == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError(
                    "CUDA was requested, but CUDA is unavailable."
                )
            return "cuda"

        return "cuda" if torch.cuda.is_available() else "cpu"

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        try:
            if self._model_loader is None:
                try:
                    from sentence_transformers import SentenceTransformer
                except ImportError as exc:
                    raise RuntimeError(
                        "Semantic retrieval requires sentence-transformers. "
                        "Install project dependencies with "
                        "'uv pip install -r requirements.txt'."
                    ) from exc

                self.device = self._resolve_device()
                logger.info(
                    "Loading embedding model %s on %s",
                    self.model_name,
                    self.device,
                )
                self._model_loader = lambda name: SentenceTransformer(
                    name,
                    device=self.device,
                )
            else:
                logger.info("Loading embedding model %s", self.model_name)

            self._model = self._model_loader(self.model_name)

            if hasattr(self._model, "get_embedding_dimension"):
                dimension = self._model.get_embedding_dimension()
            else:
                dimension = self._model.get_sentence_embedding_dimension()

            if not isinstance(dimension, int) or dimension <= 0:
                raise ValueError("model reported an invalid embedding dimension")

            self._dimension = dimension

        except Exception as exc:
            self._model = None
            self._dimension = None
            raise RuntimeError(
                f"Could not load embedding model {self.model_name!r}: {exc}"
            ) from exc

        return self._model

    @property
    def dimension(self) -> int:
        self._load_model()
        return self._dimension

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        if any(not isinstance(text, str) for text in texts):
            raise TypeError("Embedding input must contain only strings")

        model = self._load_model()

        try:
            encoded = model.encode(
                list(texts),
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            vectors = [
                normalize_vector(
                    vector.tolist() if hasattr(vector, "tolist") else vector
                )
                for vector in encoded
            ]

        except Exception as exc:
            raise RuntimeError(
                f"Could not encode text with model {self.model_name!r}: {exc}"
            ) from exc

        if len(vectors) != len(texts):
            raise RuntimeError(
                "Embedding model returned a different number of vectors "
                "than inputs"
            )

        if any(len(vector) != self._dimension for vector in vectors):
            raise RuntimeError(
                f"Embedding model {self.model_name!r} returned inconsistent "
                "vector dimensions"
            )

        return vectors

    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("Query must not be empty")
        return self.embed_texts([query])[0]

    def embed_chunks(
        self,
        chunks: Sequence[DocumentChunk],
    ) -> list[list[float]]:
        return self.embed_texts([chunk.text for chunk in chunks])
