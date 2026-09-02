from __future__ import annotations

import sqlite3
from pathlib import Path


class SearchStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            path TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            content_sha256 TEXT NOT NULL,
            indexed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
            path UNINDEXED, title, content
        );
        """)
        self.connection.commit()

    def upsert(self, path: str, title: str, content: str, sha256: str) -> None:
        self.connection.execute("DELETE FROM documents_fts WHERE path = ?", (path,))
        self.connection.execute("""INSERT INTO documents(path,title,content,content_sha256)
            VALUES(?,?,?,?) ON CONFLICT(path) DO UPDATE SET title=excluded.title,
            content=excluded.content, content_sha256=excluded.content_sha256,
            indexed_at=CURRENT_TIMESTAMP""", (path, title, content, sha256))
        self.connection.execute("INSERT INTO documents_fts(path,title,content) VALUES(?,?,?)", (path,title,content))
        self.connection.commit()

    def search(self, query: str, limit: int = 10) -> list[sqlite3.Row]:
        return list(self.connection.execute("""SELECT path, title,
            snippet(documents_fts, 2, '[', ']', '...', 24) AS snippet
            FROM documents_fts WHERE documents_fts MATCH ? LIMIT ?""", (query, limit)))

    def close(self) -> None:
        self.connection.close()
