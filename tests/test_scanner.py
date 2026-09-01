from pathlib import Path


def test_scan_and_persist_source(tmp_path: Path):
    source = tmp_path / "notes.txt"
    source.write_text("hello", encoding="utf-8")
    from ts_knowledge_agent.services.scanner import scan_directory
    files = scan_directory(tmp_path)
    assert len(files) == 1
    assert files[0].relative_path == "notes.txt"
    assert len(files[0].sha256) == 64

    from ts_knowledge_agent.repositories.state_store import StateStore
    store = StateStore(tmp_path / "state.sqlite3")
    try:
        store.upsert_source(files[0])
        rows = store.list_sources()
        assert len(rows) == 1
        assert rows[0]["sha256"] == files[0].sha256
    finally:
        store.close()
