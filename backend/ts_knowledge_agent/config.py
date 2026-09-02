from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess

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
    workspace: str
    source_root: Path
    knowledge_repo: Path
    scan_interval_minutes: int = DEFAULT_SCAN_INTERVAL_MINUTES
    git_remote: str = DEFAULT_GIT_REMOTE
    workdir: Path = Path(".local")

    @property
    def member_id(self) -> str:
        """Backward-compatible read-only alias for workspace."""
        return self.workspace

    @classmethod
    def from_env(cls) -> "Settings":
        workdir = Path(os.getenv("TS_KB_WORKDIR", ".local")).expanduser()
        config_path = Path(os.getenv("TS_KB_CONFIG", str(workdir / "ts-kb.json"))).expanduser()
        if config_path.is_file():
            settings = cls.from_file(config_path)
        else:
            settings = cls(
                workspace=(os.getenv("TS_KB_WORKSPACE") or os.getenv("TS_KB_MEMBER_ID", "local")).strip() or "local",
                source_root=Path(os.getenv("TS_KB_SOURCE_ROOT", ".")).expanduser(),
                knowledge_repo=Path(os.getenv("TS_KB_KNOWLEDGE_REPO", str(workdir / "knowledge-base" / "ts-knowledge-base"))).expanduser(),
                scan_interval_minutes=parse_interval_minutes(os.getenv("TS_KB_SCAN_INTERVAL_MINUTES")),
                git_remote=os.getenv("TS_KB_GIT_REMOTE", DEFAULT_GIT_REMOTE).strip() or DEFAULT_GIT_REMOTE,
                workdir=workdir,
            )
        return settings.with_env_overrides()

    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        workdir = Path(data["workdir"]).expanduser()
        return cls(
            workspace=data.get("workspace", data.get("member_id", "local")),
            source_root=Path(data["source_root"]).expanduser(),
            knowledge_repo=Path(data.get("knowledge_repo", str(workdir / "knowledge-base" / "ts-knowledge-base"))).expanduser(),
            scan_interval_minutes=parse_interval_minutes(str(data.get("scan_interval_minutes", 60))),
            git_remote=data.get("git_remote", DEFAULT_GIT_REMOTE),
            workdir=workdir,
        )

    def with_env_overrides(self) -> "Settings":
        return Settings(
            workspace=os.getenv("TS_KB_WORKSPACE", os.getenv("TS_KB_MEMBER_ID", self.workspace)),
            source_root=Path(os.getenv("TS_KB_SOURCE_ROOT", str(self.source_root))).expanduser(),
            knowledge_repo=Path(os.getenv("TS_KB_KNOWLEDGE_REPO", str(self.knowledge_repo))).expanduser(),
            scan_interval_minutes=parse_interval_minutes(os.getenv("TS_KB_SCAN_INTERVAL_MINUTES", str(self.scan_interval_minutes))),
            git_remote=os.getenv("TS_KB_GIT_REMOTE", self.git_remote),
            workdir=Path(os.getenv("TS_KB_WORKDIR", str(self.workdir))).expanduser(),
        )

    def write_file(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "workspace": self.workspace,
            "source_root": str(self.source_root),
            "workdir": str(self.workdir),
            "knowledge_repo": str(self.knowledge_repo),
            "scan_interval_minutes": self.scan_interval_minutes,
            "git_remote": self.git_remote,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clone_knowledge_repo(settings: Settings) -> None:
    settings.knowledge_repo.parent.mkdir(parents=True, exist_ok=True)
    if (settings.knowledge_repo / ".git").exists():
        return
    if settings.knowledge_repo.exists() and any(settings.knowledge_repo.iterdir()):
        raise RuntimeError(f"knowledge repo path is not empty: {settings.knowledge_repo}")
    result = subprocess.run(
        ["git", "clone", settings.git_remote, str(settings.knowledge_repo)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
