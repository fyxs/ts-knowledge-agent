from pathlib import Path


def test_mark_missing_sources(tmp_path: Path):
    from ts_knowledge_agent.repositories.state_store import StateStore
    from ts_knowledge_agent.services.scanner import scan_directory
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "keep.txt").write_text("keep", encoding="utf-8")
    (source_root / "remove.txt").write_text("remove", encoding="utf-8")
    store = StateStore(tmp_path / "state.sqlite3")
    try:
        for source in scan_directory(source_root):
            store.upsert_source(source)
        (source_root / "remove.txt").unlink()
        assert store.mark_missing_sources({"keep.txt"}) == 1
        rows = {row["relative_path"]: row["status"] for row in store.list_sources()}
        assert rows["remove.txt"] == "source_missing"
    finally:
        store.close()
