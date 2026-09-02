from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyncResult:
    status: str
    commit: str | None = None
    message: str | None = None


class GitSyncError(RuntimeError):
    pass


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        raise GitSyncError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def prepare_repository(repo: Path) -> SyncResult:
    """Update a clean local clone before the pipeline writes into it."""
    repo = repo.expanduser().resolve()
    if not (repo / ".git").exists():
        return SyncResult("not_initialized", message=str(repo))
    if _git(repo, "status", "--porcelain"):
        return SyncResult("blocked_dirty_worktree")
    _git(repo, "fetch", "origin")
    branch = _git(repo, "branch", "--show-current") or "main"
    try:
        _git(repo, "merge", "--ff-only", f"origin/{branch}")
    except GitSyncError as exc:
        return SyncResult("blocked_conflict", message=str(exc))
    return SyncResult("ready")


def commit_and_push(repo: Path, message: str) -> SyncResult:
    repo = repo.expanduser().resolve()
    if not (repo / ".git").exists():
        return SyncResult("not_initialized", message=str(repo))
    if not _git(repo, "status", "--porcelain"):
        return SyncResult("clean")
    _git(repo, "add", "members")
    if not _git(repo, "diff", "--cached", "--name-only"):
        return SyncResult("clean")
    _git(repo, "commit", "-m", message)
    commit = _git(repo, "rev-parse", "HEAD")
    try:
        _git(repo, "push", "origin", "HEAD")
    except GitSyncError as exc:
        return SyncResult("push_failed", commit=commit, message=str(exc))
    return SyncResult("pushed", commit=commit)
