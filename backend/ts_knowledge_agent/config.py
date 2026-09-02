from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess

DEFAULT_SHARED_KNOWLEDGE_REPOSITORY_URL = "git@github.com:fyxs/ts-knowledge-base.git"
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
    personal_workspace: str
    shared_source_directory: Path
    working_directory: Path
    shared_knowledge_repository_directory: Path
    scan_interval_minutes: int = DEFAULT_SCAN_INTERVAL_MINUTES
    shared_knowledge_repository_url: str = DEFAULT_SHARED_KNOWLEDGE_REPOSITORY_URL

    @property
    def workspace(self) -> str:
        return self.personal_workspace

    @property
    def member_id(self) -> str:
        return self.personal_workspace

    @property
    def source_root(self) -> Path:
        return self.shared_source_directory

    @property
    def workdir(self) -> Path:
        return self.working_directory

    @property
    def knowledge_repo(self) -> Path:
        return self.shared_knowledge_repository_directory

    @property
    def git_remote(self) -> str:
        return self.shared_knowledge_repository_url

    @classmethod
    def from_env(cls) -> "Settings":
        working_directory = Path(os.getenv("TS_KB_WORKING_DIRECTORY", os.getenv("TS_KB_WORKDIR", ".local"))).expanduser()
        config_path = Path(os.getenv("TS_KB_CONFIG", str(working_directory / "ts-kb.json"))).expanduser()
        if config_path.is_file():
            settings = cls.from_file(config_path)
        else:
            settings = cls(
                personal_workspace=(os.getenv("TS_KB_PERSONAL_WORKSPACE") or os.getenv("TS_KB_WORKSPACE") or os.getenv("TS_KB_MEMBER_ID", "local")).strip() or "local",
                shared_source_directory=Path(os.getenv("TS_KB_SHARED_SOURCE_DIRECTORY", os.getenv("TS_KB_SOURCE_ROOT", "."))).expanduser(),
                working_directory=working_directory,
                shared_knowledge_repository_directory=Path(os.getenv("TS_KB_SHARED_KNOWLEDGE_REPOSITORY_DIRECTORY", os.getenv("TS_KB_KNOWLEDGE_REPO", str(working_directory / "knowledge-base" / "ts-knowledge-base")))).expanduser(),
                scan_interval_minutes=parse_interval_minutes(os.getenv("TS_KB_SCAN_INTERVAL_MINUTES")),
                shared_knowledge_repository_url=os.getenv("TS_KB_SHARED_KNOWLEDGE_REPOSITORY_URL", os.getenv("TS_KB_GIT_REMOTE", DEFAULT_SHARED_KNOWLEDGE_REPOSITORY_URL)).strip() or DEFAULT_SHARED_KNOWLEDGE_REPOSITORY_URL,
            )
        return settings.with_env_overrides()

    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        working_directory = Path(data.get("working_directory", data.get("workdir"))).expanduser()
        return cls(
            personal_workspace=data.get("personal_workspace", data.get("workspace", data.get("member_id", "local"))),
            shared_source_directory=Path(data.get("shared_source_directory", data.get("source_root"))).expanduser(),
            working_directory=working_directory,
            shared_knowledge_repository_directory=Path(data.get("shared_knowledge_repository_directory", data.get("knowledge_repo", str(working_directory / "knowledge-base" / "ts-knowledge-base")))).expanduser(),
            scan_interval_minutes=parse_interval_minutes(str(data.get("scan_interval_minutes", 60))),
            shared_knowledge_repository_url=data.get("shared_knowledge_repository_url", data.get("git_remote", DEFAULT_SHARED_KNOWLEDGE_REPOSITORY_URL)),
        )

    def with_env_overrides(self) -> "Settings":
        return Settings(
            personal_workspace=os.getenv("TS_KB_PERSONAL_WORKSPACE", os.getenv("TS_KB_WORKSPACE", os.getenv("TS_KB_MEMBER_ID", self.personal_workspace))),
            shared_source_directory=Path(os.getenv("TS_KB_SHARED_SOURCE_DIRECTORY", os.getenv("TS_KB_SOURCE_ROOT", str(self.shared_source_directory)))).expanduser(),
            working_directory=Path(os.getenv("TS_KB_WORKING_DIRECTORY", os.getenv("TS_KB_WORKDIR", str(self.working_directory)))).expanduser(),
            shared_knowledge_repository_directory=Path(os.getenv("TS_KB_SHARED_KNOWLEDGE_REPOSITORY_DIRECTORY", os.getenv("TS_KB_KNOWLEDGE_REPO", str(self.shared_knowledge_repository_directory)))).expanduser(),
            scan_interval_minutes=parse_interval_minutes(os.getenv("TS_KB_SCAN_INTERVAL_MINUTES", str(self.scan_interval_minutes))),
            shared_knowledge_repository_url=os.getenv("TS_KB_SHARED_KNOWLEDGE_REPOSITORY_URL", os.getenv("TS_KB_GIT_REMOTE", self.shared_knowledge_repository_url)),
        )

    def write_file(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "personal_workspace": self.personal_workspace,
            "shared_source_directory": str(self.shared_source_directory),
            "working_directory": str(self.working_directory),
            "shared_knowledge_repository_directory": str(self.shared_knowledge_repository_directory),
            "scan_interval_minutes": self.scan_interval_minutes,
            "shared_knowledge_repository_url": self.shared_knowledge_repository_url,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clone_knowledge_repo(settings: Settings) -> None:
    path = settings.shared_knowledge_repository_directory
    path.parent.mkdir(parents=True, exist_ok=True)
    if (path / ".git").exists():
        return
    if path.exists() and any(path.iterdir()):
        raise RuntimeError(f"shared knowledge repository directory is not empty: {path}")
    result = subprocess.run(["git", "clone", settings.shared_knowledge_repository_url, str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
