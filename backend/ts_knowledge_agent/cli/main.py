from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ts_knowledge_agent.config import Settings, clone_knowledge_repo
from ts_knowledge_agent.repositories.state_store import StateStore
from ts_knowledge_agent.services.converter import convert_file
from ts_knowledge_agent.services.indexing import search_converted
from ts_knowledge_agent.services.pipeline import run_once
from ts_knowledge_agent.services.scheduler import run_scheduler
from ts_knowledge_agent.services.scanner import scan_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ts-kb")
    sub = parser.add_subparsers(dest="command")
    init = sub.add_parser("init")
    init.add_argument("--workdir", required=True, type=Path)
    init.add_argument("--workspace", required=True, help="个人在共享知识仓中的工作空间，例如 wanghm")
    init.add_argument("--source-root", required=True, type=Path)
    init.add_argument("--interval-minutes", type=int, default=60)
    init.add_argument("--git-remote", default=None)
    sub.add_parser("status")
    scan = sub.add_parser("scan"); scan.add_argument("--source-root", type=Path)
    convert = sub.add_parser("convert"); convert.add_argument("--file", required=True, type=Path); convert.add_argument("--output", type=Path)
    run = sub.add_parser("run-once"); run.add_argument("--sync", action="store_true")
    sub.add_parser("schedule")
    search = sub.add_parser("search"); search.add_argument("query")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser(); args = parser.parse_args(argv)
    if args.command == "init":
        if args.interval_minutes < 1:
            parser.error("interval-minutes must be at least 1 minute")
        try:
            settings = Settings(
                workspace=args.workspace.strip(), source_root=args.source_root, workdir=args.workdir,
                knowledge_repo=args.workdir / "knowledge-base" / "ts-knowledge-base",
                scan_interval_minutes=args.interval_minutes, git_remote=args.git_remote or "git@github.com:fyxs/ts-knowledge-base.git",
            )
            if not settings.workspace:
                parser.error("workspace must not be empty")
            if not str(settings.source_root).strip():
                parser.error("source-root must not be empty")
            settings.workdir.mkdir(parents=True, exist_ok=True)
            clone_knowledge_repo(settings)
            settings.write_file(settings.workdir / "ts-kb.json")
            print(f"initialized workdir={settings.workdir} workspace={settings.workspace} knowledge_repo={settings.knowledge_repo} git_remote={settings.git_remote}")
            return 0
        except (ValueError, RuntimeError) as exc:
            parser.error(str(exc))
    settings = Settings.from_env()
    if args.command == "scan":
        state = StateStore(settings.knowledge_repo / "data" / "state.sqlite3")
        try:
            sources = scan_directory(args.source_root or settings.source_root)
            for source in sources: state.upsert_source(source)
            print(f"scanned={len(sources)}")
        finally: state.close()
        return 0
    if args.command == "convert":
        source = args.file.expanduser().resolve(); output = args.output or settings.knowledge_repo / "members" / settings.workspace / "converted" / f"{source.stem}.md"; result = convert_file(source, output); print(f"converted={result.output_path} bytes={result.bytes_written}"); return 0
    if args.command == "run-once":
        summary = run_once(settings, sync=args.sync); print(f"scanned={summary.scanned} converted={summary.converted} skipped={summary.skipped} failed={summary.failed} indexed={summary.indexed} sync={summary.sync_status}"); return 1 if summary.failed or summary.sync_status in {"blocked_conflict", "push_failed"} else 0
    if args.command == "schedule": return run_scheduler(settings)
    if args.command == "status":
        state = StateStore(settings.knowledge_repo / "data" / "state.sqlite3")
        try: print(f"sources={len(state.list_sources())} conversions={len(state.list_conversions())} workspace={settings.workspace}")
        finally: state.close()
        return 0
    if args.command == "search":
        for row in search_converted(settings, args.query): print(f"{row['path']} | {row['title']} | {row['snippet']}")
        return 0
    parser.print_help(); return 0
