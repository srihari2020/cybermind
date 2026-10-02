
import argparse
import logging
from pathlib import Path

from knowledge.ingestion.pipeline import SUPPORTED_EXTENSIONS
from knowledge.ingestion.service import ingest_and_save


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest local documents into CyberMind's knowledge store."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="A .txt/.md file or a directory containing documents.",
    )
    parser.add_argument(
        "--source-id",
        help=(
            "Source ID for a file; for a directory, a stable namespace "
            "prefix (defaults to the directory name)."
        ),
    )
    parser.add_argument("--title", help="Title for single-file mode.")
    parser.add_argument(
        "--publisher",
        required=True,
        help="Publisher or organization name.",
    )
    parser.add_argument("--source-url", default=None)
    parser.add_argument("--license", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/knowledge.jsonl"),
    )
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=120)
    parser.add_argument(
        "--append",
        action="store_true",
        help="Compatibility option; unrelated sources are always preserved.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.chunk_size <= 0:
        parser.error("--chunk-size must be greater than zero.")
    if args.overlap < 0 or args.overlap >= args.chunk_size:
        parser.error("--overlap must be >= 0 and smaller than --chunk-size.")

    if not args.path.exists():
        parser.error(f"Input path does not exist: {args.path}")
    if args.output.exists() and args.output.is_dir():
        parser.error(f"Output path must be a file: {args.output}")

    if args.path.is_file():
        if args.path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            parser.error(
                f"Unsupported file type: {args.path.suffix}. "
                f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
        if not args.source_id or not args.title:
            parser.error(
                "--source-id and --title are required for single-file mode."
            )
        files = [args.path]
        batch_namespace = None
    elif args.path.is_dir():
        files = sorted(
            (
                file
                for file in args.path.rglob("*")
                if file.is_file()
                and file.suffix.lower() in SUPPORTED_EXTENSIONS
            ),
            key=lambda file: (
                file.relative_to(args.path).as_posix().casefold(),
                file.relative_to(args.path).as_posix(),
            ),
        )
        batch_namespace = args.source_id or args.path.name or "root"
        if not files:
            parser.error(f"No supported documents found in {args.path}")
    else:
        parser.error("Input path must be a file or directory.")

    output_path = args.output.resolve()
    input_paths = {file_path.resolve() for file_path in files}
    if output_path in input_paths:
        parser.error("Output path must not overwrite an input document.")
    if args.path.is_dir() and output_path.suffix.lower() in SUPPORTED_EXTENSIONS:
        try:
            output_path.relative_to(args.path.resolve())
        except ValueError:
            pass
        else:
            parser.error(
                "A text output file cannot be placed inside the input directory."
            )

    total_chunks = 0
    successful_files = 0
    skipped_duplicates = 0
    failures = 0

    for file_path in files:
        if args.path.is_file():
            source_id = args.source_id
        else:
            relative_path = file_path.relative_to(args.path).as_posix()
            source_id = f"batch:{batch_namespace}/{relative_path}"
        title = args.title if args.path.is_file() else file_path.stem

        try:
            chunks = ingest_and_save(
                file_path,
                args.output,
                source_id=source_id,
                title=title,
                publisher=args.publisher,
                source_url=args.source_url,
                license=args.license,
                chunk_size=args.chunk_size,
                overlap=args.overlap,
            )
            successful_files += 1
            total_chunks += len(chunks)
            if chunks:
                print(f"Ingested: {file_path} ({len(chunks)} chunks)")
            else:
                skipped_duplicates += 1
                print(f"Skipped duplicate: {file_path}")
        except (ValueError, OSError) as exc:
            failures += 1
            logging.error("Failed to process %s: %s", file_path, exc)

    print(f"Successful files: {successful_files}")
    print(f"Skipped duplicates: {skipped_duplicates}")
    print(f"Chunks generated: {total_chunks}")
    print(f"Failed files: {failures}")
    print(f"Output file: {args.output}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
