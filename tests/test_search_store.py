from pathlib import Path


def test_search_store_strips_bom(tmp_path: Path):
    from ts_knowledge_agent.repositories.search_store import SearchStore

    store = SearchStore(tmp_path / "state.sqlite3")
    try:
        store.upsert("note.md", "\ufeffTitle", "\ufeffIndex content", "hash")
        row = store.search("Index")[0]
        assert row["title"] == "Title"
        assert "\ufeff" not in row["snippet"]
    finally:
        store.close()
