from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


DEFAULT_GIT_REMOTE = "git@github.com:fyxs/ts-knowledge-base.git"


@dataclass(frozen=True)
class Settings:
    member_id: str
    source_root: Path
    knowledge_repo: Path
    git_remote: str = DEFAULT_GIT_REMOTE

    @classmethod
    def from_env(cls) -> "Settings":
        member_id = os.getenv("TS_KB_MEMBER_ID", "local-member").strip() or "local-member"
        source_root = Path(os.getenv("TS_KB_SOURCE_ROOT", ".")).expanduser()
        knowledge_repo = Path(
            os.getenv("TS_KB_KNOWLEDGE_REPO", "./.local/ts-knowledge-base")
        ).expanduser()
        return cls(member_id, source_root, knowledge_repo)
