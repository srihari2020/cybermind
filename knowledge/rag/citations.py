import re
from dataclasses import dataclass

from knowledge.rag.context import ContextBundle


CITATION_PATTERN = re.compile(r"\[(S\d+)\]")


@dataclass(frozen=True)
class CitationValidation:
    cited_ids: tuple[str, ...]
    unknown_ids: tuple[str, ...]
    missing_required: bool

    @property
    def is_valid(self) -> bool:
        return not self.unknown_ids and not self.missing_required


def validate_citations(
    answer: str,
    context: ContextBundle,
    *,
    require_citations: bool = True,
) -> CitationValidation:
    cited_ids = tuple(
        dict.fromkeys(CITATION_PATTERN.findall(answer))
    )

    available_ids = {
        item.citation_id for item in context.evidence
    }

    unknown_ids = tuple(
        citation
        for citation in cited_ids
        if citation not in available_ids
    )

    missing_required = (
        require_citations
        and bool(context.evidence)
        and not cited_ids
    )

    return CitationValidation(
        cited_ids=cited_ids,
        unknown_ids=unknown_ids,
        missing_required=missing_required,
    )
