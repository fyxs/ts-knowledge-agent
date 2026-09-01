from pathlib import Path


def test_convert_file_writes_markdown_without_touching_source(tmp_path: Path):
    from ts_knowledge_agent.services.converter import convert_file

    source = tmp_path / "notes.txt"
    source.write_text("# Smoke note\n\nconverted content\n", encoding="utf-8")
    output = tmp_path / "repo" / "members" / "tester" / "converted" / "notes.md"

    result = convert_file(source, output)

    assert result.output_path == output.resolve()
    assert output.read_text(encoding="utf-8")
    assert source.read_text(encoding="utf-8").startswith("# Smoke note")
