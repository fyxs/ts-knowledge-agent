from pathlib import Path


def test_init_uses_workspace_name():
    from ts_knowledge_agent.cli.main import build_parser
    args = build_parser().parse_args(["init", "--workdir", "D:/work", "--workspace", "wanghm", "--source-root", "D:/source"])
    assert args.workspace == "wanghm"


def test_init_requires_workspace_and_source_root():
    from ts_knowledge_agent.cli.main import build_parser
    import pytest
    with pytest.raises(SystemExit):
        build_parser().parse_args(["init", "--workdir", "D:/work", "--source-root", "D:/source"])
    with pytest.raises(SystemExit):
        build_parser().parse_args(["init", "--workdir", "D:/work", "--workspace", "wanghm"])


def test_legacy_member_id_env_remains_compatible(monkeypatch):
    from ts_knowledge_agent.config import Settings
    monkeypatch.delenv("TS_KB_WORKSPACE", raising=False)
    monkeypatch.setenv("TS_KB_MEMBER_ID", "wanghm")
    monkeypatch.setenv("TS_KB_CONFIG", "C:/path/that/does/not/exist.json")
    assert Settings.from_env().workspace == "wanghm"


def test_settings_loads_legacy_config_key(tmp_path, monkeypatch):
    from ts_knowledge_agent.config import Settings
    config = tmp_path / "ts-kb.json"
    config.write_text('{"member_id":"m","source_root":"D:/source","workdir":"D:/work"}', encoding="utf-8")
    monkeypatch.setenv("TS_KB_CONFIG", str(config))
    assert Settings.from_env().workspace == "m"
