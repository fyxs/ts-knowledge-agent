from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ts_knowledge_agent.config import Settings
from ts_knowledge_agent.services.scanner import scan_directory
from ts_knowledge_agent.repositories.state_store import StateStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ts-kb")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status")
    scan = sub.add_parser("scan")
    scan.add_argument("--source-root", type=Path)
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
    if args.command == "status":
        state = StateStore(settings.knowledge_repo / "data" / "state.sqlite3")
        try:
            print(f"sources={len(state.list_sources())} member_id={settings.member_id}")
        finally:
            state.close()
        return 0
    if args.command == "search":
        print("ts-kb: search scaffold; implementation pending")
        return 0
    parser.print_help()
    return 0
