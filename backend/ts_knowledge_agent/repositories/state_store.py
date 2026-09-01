from __future__ import annotations

import sqlite3
from pathlib import Path
from ts_knowledge_agent.services.scanner import SourceFile


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS sources (
            relative_path TEXT PRIMARY KEY,
            size INTEGER NOT NULL,
            mtime_ns INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            status TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.connection.commit()

    def upsert_source(self, source: SourceFile, status: str = "discovered") -> None:
        self.connection.execute("""
        INSERT INTO sources(relative_path, size, mtime_ns, sha256, status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(relative_path) DO UPDATE SET
          size=excluded.size, mtime_ns=excluded.mtime_ns,
          sha256=excluded.sha256, status=excluded.status,
          updated_at=CURRENT_TIMESTAMP
        """, (source.relative_path, source.size, source.mtime_ns, source.sha256, status))
        self.connection.commit()

    def list_sources(self) -> list[sqlite3.Row]:
        return list(self.connection.execute("SELECT * FROM sources ORDER BY relative_path"))

    def close(self) -> None:
        self.connection.close()
