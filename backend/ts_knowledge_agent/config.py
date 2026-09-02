from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


DEFAULT_GIT_REMOTE = "git@github.com:fyxs/ts-knowledge-base.git"
DEFAULT_SCAN_INTERVAL_MINUTES = 60


def parse_interval_minutes(value: str | None) -> int:
    if value is None or not value.strip():
        return DEFAULT_SCAN_INTERVAL_MINUTES
    try:
        minutes = int(value)
    except ValueError as exc:
        raise ValueError("scan interval must be an integer number of minutes") from exc
    if minutes < 1:
        raise ValueError("scan interval must be at least 1 minute")
    return minutes


@dataclass(frozen=True)
class Settings:
    member_id: str
    source_root: Path
    knowledge_repo: Path
    scan_interval_minutes: int = DEFAULT_SCAN_INTERVAL_MINUTES
    git_remote: str = DEFAULT_GIT_REMOTE

    @classmethod
    def from_env(cls) -> "Settings":
        member_id = os.getenv("TS_KB_MEMBER_ID", "local-member").strip() or "local-member"
        source_root = Path(os.getenv("TS_KB_SOURCE_ROOT", ".")).expanduser()
        knowledge_repo = Path(os.getenv("TS_KB_KNOWLEDGE_REPO", "./.local/ts-knowledge-base")).expanduser()
        interval = parse_interval_minutes(os.getenv("TS_KB_SCAN_INTERVAL_MINUTES"))
        return cls(member_id, source_root, knowledge_repo, interval)
