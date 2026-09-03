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
        CREATE TABLE IF NOT EXISTS conversions (
            relative_path TEXT PRIMARY KEY,
            source_sha256 TEXT NOT NULL,
            output_path TEXT NOT NULL,
            converter_version TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
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

    def mark_missing_sources(self, seen_paths: set[str]) -> int:
        rows = self.connection.execute("SELECT relative_path FROM sources").fetchall()
        missing = [row["relative_path"] for row in rows if row["relative_path"] not in seen_paths]
        if missing:
            self.connection.executemany("UPDATE sources SET status='source_missing', updated_at=CURRENT_TIMESTAMP WHERE relative_path=?", [(path,) for path in missing])
            self.connection.commit()
        return len(missing)

    def list_sources(self) -> list[sqlite3.Row]:
        return list(self.connection.execute("SELECT * FROM sources ORDER BY relative_path"))

    def needs_conversion(self, source: SourceFile) -> bool:
        row = self.connection.execute("SELECT source_sha256, status FROM conversions WHERE relative_path = ?", (source.relative_path,)).fetchone()
        return row is None or row["source_sha256"] != source.sha256 or row["status"] != "converted"

    def record_conversion(self, relative_path: str, source_sha256: str, output_path: Path, converter_version: str, status: str, error_message: str | None = None) -> None:
        self.connection.execute("""
        INSERT INTO conversions(relative_path, source_sha256, output_path, converter_version, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(relative_path) DO UPDATE SET
          source_sha256=excluded.source_sha256, output_path=excluded.output_path,
          converter_version=excluded.converter_version, status=excluded.status,
          error_message=excluded.error_message, updated_at=CURRENT_TIMESTAMP
        """, (relative_path, source_sha256, str(output_path), converter_version, status, error_message))
        self.connection.commit()

    def list_conversions(self) -> list[sqlite3.Row]:
        return list(self.connection.execute("SELECT * FROM conversions ORDER BY relative_path"))

    def close(self) -> None:
        self.connection.close()
