import argparse
import os
import sys

from knowledge.rag.providers import (
    OllamaChatProvider,
    OllamaProviderError,
)
from knowledge.rag.service import RAGService
from knowledge.retrieval.service import SemanticRetrievalService


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ask cybersecurity questions using CyberMind RAG."
    )

    parser.add_argument("question", help="Cybersecurity question")

    parser.add_argument(
        "--store",
        default=os.getenv(
            "CYBERMIND_KNOWLEDGE_STORE",
            "data/processed/knowledge.jsonl",
        ),
    )
    parser.add_argument(
        "--index",
        default=os.getenv(
            "CYBERMIND_VECTOR_INDEX",
            "data/processed/knowledge.index.json",
        ),
    )
    parser.add_argument("--model", default="qwen3.5:4b")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-similarity", type=float)

    args = parser.parse_args()

    try:
        retrieval = SemanticRetrievalService(
            store_path=args.store,
            index_path=args.index,
        )

        provider = OllamaChatProvider(model=args.model)

        rag = RAGService(
            retrieval,
            provider,
            top_k=args.top_k,
            min_similarity=args.min_similarity,
        )

        result = rag.answer(args.question)

        print("\n========== CYBERMIND ==========\n")
        print(result.answer)

        if result.evidence:
            print("\n========== SOURCES ==========\n")

            for item in result.evidence:
                print(
                    f"[{item.citation_id}] {item.title} "
                    f"| {item.publisher} "
                    f"| Similarity: {item.similarity:.4f}"
                )

        if result.model:
            print("\n========== PERFORMANCE ==========\n")
            print(f"Model: {result.model}")
            print(f"Total time: {result.total_duration:.3f}s")
            print(f"Model loading: {result.load_duration:.3f}s")
            print(f"Generation: {result.generation_duration:.3f}s")
            print(f"Generated tokens: {result.eval_count}")
            print(f"Speed: {result.tokens_per_second:.2f} tokens/s")

        print("\n===============================\n")

        return 1 if result.abstained else 0

    except (OllamaProviderError, OSError, ValueError) as exc:
        print(f"CyberMind error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
