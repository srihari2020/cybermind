from dataclasses import dataclass
from typing import Sequence

from knowledge.retrieval.service import RetrievalResult


@dataclass(frozen=True)
class Evidence:
    citation_id: str
    source_id: str
    chunk_id: str
    title: str
    publisher: str
    similarity: float
    text: str


@dataclass(frozen=True)
class ContextBundle:
    evidence: tuple[Evidence, ...]

    @property
    def is_empty(self) -> bool:
        return not self.evidence

    def render(self) -> str:
        sections = []

        for item in self.evidence:
            sections.append(
                f"[{item.citation_id}]\n"
                f"Title: {item.title}\n"
                f"Publisher: {item.publisher}\n"
                f"Source ID: {item.source_id}\n"
                f"Chunk ID: {item.chunk_id}\n"
                f"Similarity: {item.similarity:.4f}\n"
                f"Evidence:\n{item.text}"
            )

        return "\n\n---\n\n".join(sections)


def build_context(
    results: Sequence[RetrievalResult],
) -> ContextBundle:
    evidence = []

    for rank, result in enumerate(results, start=1):
        chunk = result.chunk

        evidence.append(
            Evidence(
                citation_id=f"S{rank}",
                source_id=result.source_id,
                chunk_id=result.chunk_id,
                title=result.title,
                publisher=result.publisher,
                similarity=result.similarity,
                text=chunk.text,
            )
        )

    return ContextBundle(evidence=tuple(evidence))
