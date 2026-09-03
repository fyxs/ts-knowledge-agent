from pathlib import Path


def test_plan_batches_is_deterministic():
    from ts_knowledge_agent.services.pipeline import plan_batches
    from ts_knowledge_agent.services.scanner import SourceFile
    def source(name): return SourceFile(name, Path(name), 1, 1, name)
    batches = plan_batches([source("c.txt"), source("a.txt"), source("b.txt")], 2)
    assert [[f.relative_path for f in b.files] for b in batches] == [["a.txt", "b.txt"], ["c.txt"]]
    assert [b.number for b in batches] == [1, 2]


def test_run_once_processes_pending_files_by_batch(tmp_path):
    from ts_knowledge_agent.config import Settings
    from ts_knowledge_agent.services.pipeline import run_once
    source_root = tmp_path / "source"; repo = tmp_path / "repo"
    source_root.mkdir(); (source_root / "a.txt").write_text("a", encoding="utf-8"); (source_root / "b.txt").write_text("b", encoding="utf-8"); (source_root / "c.txt").write_text("c", encoding="utf-8")
    settings = Settings("wanghm", source_root, tmp_path, repo, 60, "unused")
    class Fake:
        def convert(self, source): return source.read_text(encoding="utf-8")
    batches=[]; summary = run_once(settings, batch_size=2, converter=Fake(), on_batch=lambda b: batches.append(b.number))
    assert (summary.queued, summary.batches, summary.converted) == (3, 2, 3)
    assert batches == [1, 2]
