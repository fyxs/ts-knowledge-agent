from __future__ import annotations

import hashlib
from pathlib import Path
from ts_knowledge_agent.config import Settings
from ts_knowledge_agent.repositories.search_store import SearchStore


def index_converted(settings: Settings) -> int:
    root = settings.shared_knowledge_repository_directory / "members" / settings.personal_workspace 
    store = SearchStore(settings.shared_knowledge_repository_directory / "data" / "state.sqlite3")
    count = 0
    try:
        if not root.exists():
            return 0
        for path in sorted(root.rglob("*.md")):
            content = path.read_text(encoding="utf-8")
            title = next((line[2:].strip() for line in content.splitlines() if line.startswith("# ")), path.stem)
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            store.upsert(str(path.relative_to(settings.shared_knowledge_repository_directory)), title, content, digest)
            count += 1
        return count
    finally:
        store.close()


def search_converted(settings: Settings, query: str) -> list[dict[str, str]]:
    store = SearchStore(settings.shared_knowledge_repository_directory / "data" / "state.sqlite3")
    try:
        return [dict(row) for row in store.search(query)]
    finally:
        store.close()
