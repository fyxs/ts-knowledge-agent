from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ts_knowledge_agent.adapters.git_sync import commit_and_push, prepare_repository
from ts_knowledge_agent.config import Settings
from ts_knowledge_agent.repositories.state_store import StateStore
from ts_knowledge_agent.services.converter import CONVERTER_VERSION, convert_file
from ts_knowledge_agent.services.indexing import index_converted
from ts_knowledge_agent.services.scanner import scan_directory


@dataclass(frozen=True)
class RunSummary:
    scanned: int
    converted: int
    skipped: int
    failed: int
    indexed: int = 0
    sync_status: str = "disabled"


def output_path_for(settings: Settings, relative_path: str) -> Path:
    relative = Path(relative_path)
    return settings.knowledge_repo / "members" / settings.member_id / "converted" / relative.with_suffix(".md")


def run_once(settings: Settings, sync: bool = False) -> RunSummary:
    state = StateStore(settings.knowledge_repo / "data" / "state.sqlite3")
    converted = skipped = failed = 0
    sync_status = "disabled"
    try:
        prepared = prepare_repository(settings.knowledge_repo) if sync else None
        if prepared is not None and prepared.status != "ready":
            return RunSummary(0, 0, 0, 0, 0, prepared.status)
        sources = scan_directory(settings.source_root)
        for source in sources:
            state.upsert_source(source)
            output = output_path_for(settings, source.relative_path)
            if not state.needs_conversion(source):
                skipped += 1
                continue
            try:
                result = convert_file(source.absolute_path, output)
                state.record_conversion(source.relative_path, source.sha256, result.output_path, CONVERTER_VERSION, "converted")
                converted += 1
            except Exception as exc:
                state.record_conversion(source.relative_path, source.sha256, output, CONVERTER_VERSION, "failed", str(exc))
                failed += 1
        indexed = index_converted(settings)
        if sync and failed == 0:
            sync_status = commit_and_push(settings.knowledge_repo, "Update converted knowledge").status
        return RunSummary(len(sources), converted, skipped, failed, indexed, sync_status)
    finally:
        state.close()
