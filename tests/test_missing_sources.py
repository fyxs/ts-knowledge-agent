from pathlib import Path


def test_mark_missing_sources(tmp_path: Path):
    from ts_knowledge_agent.repositories.state_store import StateStore
    from ts_knowledge_agent.services.scanner import scan_directory
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    (tmp_path / "remove.txt").write_text("remove", encoding="utf-8")
    store = StateStore(tmp_path / "state.sqlite3")
    try:
        for source in scan_directory(tmp_path):
            store.upsert_source(source)
        (tmp_path / "remove.txt").unlink()
        assert store.mark_missing_sources({"keep.txt"}) == 1
        rows = {row["relative_path"]: row["status"] for row in store.list_sources()}
        assert rows["remove.txt"] == "source_missing"
    finally:
        store.close()
