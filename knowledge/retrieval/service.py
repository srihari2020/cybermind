import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from knowledge.ingestion.models import DocumentChunk
from knowledge.ingestion.storage import load_chunks, unique_chunks
from knowledge.retrieval.embeddings import SentenceTransformerEmbeddings
from knowledge.retrieval.index import PersistentVectorIndex, VectorEntry


@dataclass(frozen=True)
class RetrievalResult:
    chunk: DocumentChunk
    similarity: float

    @property
    def source_id(self) -> str:
        return self.chunk.source_id

    @property
    def title(self) -> str:
        return self.chunk.metadata.title

    @property
    def publisher(self) -> str:
        return self.chunk.metadata.publisher

    @property
    def chunk_id(self) -> str:
        return self.chunk.chunk_id


@dataclass(frozen=True)
class IndexingSummary:
    indexed: int
    reused: int
    removed: int


class SemanticRetrievalService:
    def __init__(
        self,
        store_path: str | Path,
        index_path: str | Path,
        *,
        embeddings=None,
    ) -> None:
        self.store_path = Path(store_path)
        self.embeddings = embeddings or SentenceTransformerEmbeddings()
        self.index = PersistentVectorIndex(index_path)

    def index_chunks(
        self,
        chunks: Sequence[DocumentChunk] | None = None,
        *,
        rebuild: bool = False,
    ) -> IndexingSummary:
        source_chunks = load_chunks(self.store_path) if chunks is None else list(chunks)
        source_chunks = unique_chunks(source_chunks)
        if not rebuild:
            self.index.validate_model_name(self.embeddings.model_name)

        previous = {
            (entry.source_id, entry.chunk_id): entry
            for entry in self.index.entries
        }
        current_keys = {(chunk.source_id, chunk.chunk_id) for chunk in source_chunks}
        to_embed = []
        replacement: list[VectorEntry] = []
        reused = 0

        for chunk in source_chunks:
            key = (chunk.source_id, chunk.chunk_id)
            content_hash = hashlib.sha256(chunk.text.encode("utf-8")).hexdigest()
            existing = previous.get(key)
            if (
                existing is not None
                and existing.content_hash == content_hash
                and not rebuild
            ):
                replacement.append(
                    VectorEntry(
                        source_id=chunk.source_id,
                        chunk_id=chunk.chunk_id,
                        title=chunk.metadata.title,
                        publisher=chunk.metadata.publisher,
                        content_hash=content_hash,
                        vector=existing.vector,
                    )
                )
                reused += 1
            else:
                to_embed.append(chunk)

        vectors = self.embeddings.embed_chunks(to_embed) if to_embed else []
        if len(vectors) != len(to_embed):
            raise RuntimeError(
                "Embedding provider returned a different number of vectors "
                "than chunks"
            )
        for chunk, vector in zip(to_embed, vectors):
            replacement.append(
                VectorEntry(
                    source_id=chunk.source_id,
                    chunk_id=chunk.chunk_id,
                    title=chunk.metadata.title,
                    publisher=chunk.metadata.publisher,
                    content_hash=hashlib.sha256(
                        chunk.text.encode("utf-8")
                    ).hexdigest(),
                    vector=tuple(vector),
                )
            )

        dimension = (
            len(vectors[0])
            if vectors
            else None if rebuild else self.index.dimension
        )
        self.index.replace(
            replacement,
            model_name=self.embeddings.model_name,
            dimension=dimension,
            allow_model_change=rebuild,
        )
        return IndexingSummary(
            indexed=len(to_embed),
            reused=reused,
            removed=len(set(previous) - current_keys),
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float | None = None,
    ) -> list[RetrievalResult]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")
        if min_similarity is not None and not -1 <= min_similarity <= 1:
            raise ValueError("min_similarity must be between -1 and 1")
        self.index.validate_model_name(self.embeddings.model_name)
        if not query.strip() or not self.index.entries:
            return []

        query_vector = self.embeddings.embed_query(query)
        matches = self.index.search(
            query_vector,
            top_k=None,
            min_similarity=min_similarity,
        )
        chunks_by_key = {
            (chunk.source_id, chunk.chunk_id): chunk
            for chunk in load_chunks(self.store_path)
        }
        results = []
        for match in matches:
            chunk = chunks_by_key.get((match.source_id, match.chunk_id))
            if chunk is not None:
                results.append(RetrievalResult(chunk, match.similarity))
                if len(results) == top_k:
                    break
        return results
