import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from knowledge.retrieval.vectors import normalize_vector


INDEX_FORMAT_VERSION = 1
SIMILARITY_METRIC = "cosine"


@dataclass(frozen=True)
class VectorEntry:
    source_id: str
    chunk_id: str
    title: str
    publisher: str
    content_hash: str
    vector: tuple[float, ...]


@dataclass(frozen=True)
class VectorMatch:
    source_id: str
    chunk_id: str
    similarity: float


class PersistentVectorIndex:
    """Small JSON-backed exact cosine index for local knowledge stores."""

    def __init__(
        self,
        file_path: str | Path,
        *,
        model_name: str | None = None,
    ) -> None:
        self.file_path = Path(file_path)
        self.model_name = model_name
        self.dimension: int | None = None
        self._entries: dict[tuple[str, str], VectorEntry] = {}
        if self.file_path.exists():
            self._load()
        if model_name is not None:
            self.validate_model_name(model_name)

    @property
    def entries(self) -> tuple[VectorEntry, ...]:
        return tuple(self._entries.values())

    def validate_model_name(self, model_name: str) -> None:
        if self.model_name is not None and self.model_name != model_name:
            raise ValueError(
                f"Index uses embedding model {self.model_name!r}, but "
                f"{model_name!r} was requested. Rebuild the index to change models."
            )
        self.model_name = model_name

    def _load(self) -> None:
        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("vector index must contain a JSON object")
            if payload.get("format_version") != INDEX_FORMAT_VERSION:
                raise ValueError("unsupported vector index format version")
            if payload.get("metric") != SIMILARITY_METRIC:
                raise ValueError("unsupported vector index similarity metric")
            stored_dimension = payload.get("dimension")
            if stored_dimension is not None and (
                not isinstance(stored_dimension, int) or stored_dimension <= 0
            ):
                raise ValueError("invalid vector dimension in index")

            records = payload.get("records")
            if not isinstance(records, list):
                raise ValueError("vector index records must be a list")
            entries = {}
            for record in records:
                vector = normalize_vector(record["vector"])
                if stored_dimension is None or len(vector) != stored_dimension:
                    raise ValueError("vector dimension does not match index")
                entry = VectorEntry(
                    source_id=record["source_id"],
                    chunk_id=record["chunk_id"],
                    title=record["title"],
                    publisher=record["publisher"],
                    content_hash=record["content_hash"],
                    vector=tuple(vector),
                )
                key = (entry.source_id, entry.chunk_id)
                if key in entries:
                    raise ValueError(f"duplicate vector record for {key!r}")
                entries[key] = entry

            self.model_name = payload.get("model_name")
            self.dimension = stored_dimension
            self._entries = entries
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ValueError(
                f"Could not read vector index {self.file_path}: {exc}"
            ) from exc

    def replace(
        self,
        entries: Sequence[VectorEntry],
        *,
        model_name: str,
        dimension: int | None,
        allow_model_change: bool = False,
    ) -> None:
        if dimension is not None and dimension <= 0:
            raise ValueError("Vector dimension must be greater than zero")
        if (
            self.model_name is not None
            and self.model_name != model_name
            and not allow_model_change
        ):
            raise ValueError(
                f"Index uses embedding model {self.model_name!r}, but "
                f"{model_name!r} was requested. Rebuild the index to change models."
            )
        if (
            self.dimension is not None
            and dimension is not None
            and self.dimension != dimension
            and not allow_model_change
        ):
            raise ValueError(
                f"Index dimension is {self.dimension}, but received {dimension}. "
                "Rebuild the index to change embedding dimensions."
            )

        replacement = {}
        for entry in entries:
            vector = normalize_vector(entry.vector)
            if dimension is None or len(vector) != dimension:
                raise ValueError("Vector dimension does not match index configuration")
            normalized = VectorEntry(
                source_id=entry.source_id,
                chunk_id=entry.chunk_id,
                title=entry.title,
                publisher=entry.publisher,
                content_hash=entry.content_hash,
                vector=tuple(vector),
            )
            key = (normalized.source_id, normalized.chunk_id)
            previous = replacement.get(key)
            if previous is not None and previous != normalized:
                raise ValueError(f"Conflicting vector records share key {key!r}")
            replacement[key] = normalized

        previous_model_name = self.model_name
        previous_dimension = self.dimension
        previous_entries = self._entries
        self.model_name = model_name
        self.dimension = dimension
        self._entries = replacement
        try:
            self._save()
        except OSError:
            self.model_name = previous_model_name
            self.dimension = previous_dimension
            self._entries = previous_entries
            raise

    def search(
        self,
        query_vector: Sequence[float],
        *,
        top_k: int | None = 5,
        min_similarity: float | None = None,
    ) -> list[VectorMatch]:
        if top_k is not None and top_k <= 0:
            raise ValueError("top_k must be greater than zero")
        if min_similarity is not None and not -1 <= min_similarity <= 1:
            raise ValueError("min_similarity must be between -1 and 1")
        if not self._entries:
            return []

        query = normalize_vector(query_vector)
        if len(query) != self.dimension:
            raise ValueError(
                f"Query vector dimension is {len(query)}, but index dimension "
                f"is {self.dimension}"
            )

        matches = []
        for entry in self._entries.values():
            similarity = sum(
                query_value * entry_value
                for query_value, entry_value in zip(query, entry.vector)
            )
            if min_similarity is None or similarity >= min_similarity:
                matches.append(
                    VectorMatch(entry.source_id, entry.chunk_id, similarity)
                )
        matches.sort(key=lambda match: (-match.similarity, match.source_id, match.chunk_id))
        return matches if top_k is None else matches[:top_k]

    def _save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format_version": INDEX_FORMAT_VERSION,
            "model_name": self.model_name,
            "dimension": self.dimension,
            "metric": SIMILARITY_METRIC,
            "records": [
                {
                    "source_id": entry.source_id,
                    "chunk_id": entry.chunk_id,
                    "title": entry.title,
                    "publisher": entry.publisher,
                    "content_hash": entry.content_hash,
                    "vector": list(entry.vector),
                }
                for entry in sorted(
                    self._entries.values(),
                    key=lambda item: (item.source_id, item.chunk_id),
                )
            ],
        }
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=self.file_path.parent,
                prefix=f".{self.file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                json.dump(payload, file, ensure_ascii=False, separators=(",", ":"))
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_path, self.file_path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
