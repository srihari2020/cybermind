import argparse
import logging
import os
from pathlib import Path

from knowledge.retrieval.embeddings import (
    DEFAULT_MODEL_NAME,
    SentenceTransformerEmbeddings,
)
from knowledge.retrieval.service import SemanticRetrievalService


DEFAULT_STORE = Path(
    os.environ.get("CYBERMIND_KNOWLEDGE_STORE", "data/processed/knowledge.jsonl")
)
DEFAULT_INDEX = Path(
    os.environ.get("CYBERMIND_VECTOR_INDEX", "data/processed/knowledge.index.json")
)


def _add_paths_and_model(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument(
        "--model",
        default=os.environ.get("CYBERMIND_EMBEDDING_MODEL", DEFAULT_MODEL_NAME),
        help="Sentence-transformers model name (or CYBERMIND_EMBEDDING_MODEL).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and search CyberMind's local semantic knowledge index."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    index_parser = commands.add_parser(
        "index",
        help="Build or update vectors from the JSONL knowledge store.",
    )
    _add_paths_and_model(index_parser)
    index_parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Re-embed every chunk and allow changing the model configuration.",
    )

    search_parser = commands.add_parser(
        "search",
        help="Search indexed chunks by semantic similarity.",
    )
    search_parser.add_argument("query", help="Natural-language search query.")
    _add_paths_and_model(search_parser)
    search_parser.add_argument("--top-k", type=int, default=5)
    search_parser.add_argument(
        "--min-similarity",
        type=float,
        default=None,
        help="Minimum cosine similarity in [-1, 1]; omit to return nearest matches.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.command == "search":
        if args.top_k <= 0:
            parser.error("--top-k must be greater than zero.")
        if args.min_similarity is not None and not -1 <= args.min_similarity <= 1:
            parser.error("--min-similarity must be between -1 and 1.")
    if not args.store.is_file():
        parser.error(f"Knowledge store does not exist or is not a file: {args.store}")
    if args.index.exists() and args.index.is_dir():
        parser.error(f"Vector index path must be a file: {args.index}")

    try:
        service = SemanticRetrievalService(
            args.store,
            args.index,
            embeddings=SentenceTransformerEmbeddings(args.model),
        )
        if args.command == "index":
            summary = service.index_chunks(rebuild=args.rebuild)
            print(
                f"Indexed {summary.indexed} chunks; reused {summary.reused} "
                f"vectors; removed {summary.removed} stale entries."
            )
            print(f"Vector index: {args.index}")
            return 0

        results = service.search(
            args.query,
            top_k=args.top_k,
            min_similarity=args.min_similarity,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))

    if not results:
        print("No matching chunks found.")
        return 0

    for rank, result in enumerate(results, start=1):
        chunk = result.chunk
        print(
            f"[{rank}] similarity={result.similarity:.4f} "
            f"source_id={chunk.source_id} chunk_id={chunk.chunk_id}"
        )
        print(f"Title: {chunk.metadata.title}")
        print(f"Publisher: {chunk.metadata.publisher}")
        print(chunk.text)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
