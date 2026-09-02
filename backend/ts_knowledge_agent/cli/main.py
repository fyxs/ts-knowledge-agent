from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ts_knowledge_agent.config import Settings
from ts_knowledge_agent.repositories.state_store import StateStore
from ts_knowledge_agent.services.converter import convert_file
from ts_knowledge_agent.services.pipeline import run_once
from ts_knowledge_agent.services.scheduler import run_scheduler
from ts_knowledge_agent.services.scanner import scan_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ts-kb")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status")
    scan = sub.add_parser("scan")
    scan.add_argument("--source-root", type=Path)
    convert = sub.add_parser("convert")
    convert.add_argument("--file", required=True, type=Path)
    convert.add_argument("--output", type=Path)
    sub.add_parser("run-once")
    sub.add_parser("schedule")
    search = sub.add_parser("search")
    search.add_argument("query", nargs="*")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    if args.command == "scan":
        root = args.source_root or settings.source_root
        state = StateStore(settings.knowledge_repo / "data" / "state.sqlite3")
        try:
            sources = scan_directory(root)
            for source in sources:
                state.upsert_source(source)
            print(f"scanned={len(sources)} source_root={root}")
        finally:
            state.close()
        return 0
    if args.command == "convert":
        source = args.file.expanduser().resolve()
        output = args.output or settings.knowledge_repo / "members" / settings.member_id / "converted" / f"{source.stem}.md"
        result = convert_file(source, output)
        print(f"converted={result.output_path} bytes={result.bytes_written}")
        return 0
    if args.command == "run-once":
        summary = run_once(settings)
        print(f"scanned={summary.scanned} converted={summary.converted} skipped={summary.skipped} failed={summary.failed}")
        return 1 if summary.failed else 0
    if args.command == "schedule":
        return run_scheduler(settings)
    if args.command == "status":
        state = StateStore(settings.knowledge_repo / "data" / "state.sqlite3")
        try:
            print(f"sources={len(state.list_sources())} conversions={len(state.list_conversions())} member_id={settings.member_id}")
        finally:
            state.close()
        return 0
    if args.command == "search":
        print("ts-kb: search scaffold; implementation pending")
        return 0
    parser.print_help()
    return 0
