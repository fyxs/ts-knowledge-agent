from pathlib import Path


def test_settings_requires_explicit_configuration(tmp_path, monkeypatch):
    from ts_knowledge_agent.config import Settings
    monkeypatch.setenv("TS_KB_CONFIG", str(tmp_path / "missing.json"))
    import pytest
    with pytest.raises(FileNotFoundError):
        Settings.from_env()


def test_settings_reads_canonical_configuration(tmp_path):
    from ts_knowledge_agent.config import Settings
    config = tmp_path / "ts-kb.json"
    config.write_text('{"personal_workspace":"wanghm","shared_source_directory":"D:/source","working_directory":"D:/work","shared_knowledge_repository_directory":"D:/work/kb","shared_knowledge_repository_url":"ssh://example/kb.git","scan_interval_minutes":7}', encoding="utf-8")
    settings = Settings.from_file(config)
    assert settings.personal_workspace == "wanghm"
    assert settings.shared_knowledge_repository_url == "ssh://example/kb.git"
    assert settings.scan_interval_minutes == 7
