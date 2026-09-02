from __future__ import annotations

from pathlib import Path


def test_init_requires_workdir():
    from ts_knowledge_agent.cli.main import build_parser
    import pytest
    with pytest.raises(SystemExit):
        build_parser().parse_args(["init", "--member-id", "m", "--source-root", "."])


def test_settings_loads_workdir_config(tmp_path: Path, monkeypatch):
    from ts_knowledge_agent.config import Settings
    config = tmp_path / "ts-kb.json"
    config.write_text('{"member_id":"m","source_root":"D:/source","workdir":"D:/work","scan_interval_minutes":5}', encoding="utf-8")
    monkeypatch.setenv("TS_KB_CONFIG", str(config))
    settings = Settings.from_env()
    assert settings.member_id == "m"
    assert settings.workdir == Path("D:/work")
    assert settings.knowledge_repo == Path("D:/work/knowledge-base/ts-knowledge-base")
    assert settings.git_remote == "git@github.com:fyxs/ts-knowledge-base.git"
