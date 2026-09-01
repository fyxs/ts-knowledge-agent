import hashlib
from pathlib import Path


def test_sha256_and_scan_are_deterministic(tmp_path: Path):
    (tmp_path / "b.txt").write_text("B", encoding="utf-8")
    (tmp_path / "a.txt").write_text("A", encoding="utf-8")
    from ts_knowledge_agent.services.scanner import scan_directory
    result = scan_directory(tmp_path)
    assert [item.relative_path for item in result] == ["a.txt", "b.txt"]
    assert result[0].sha256 == hashlib.sha256(b"A").hexdigest()


def test_conversion_never_overwrites_source(tmp_path: Path):
    from ts_knowledge_agent.services.converter import convert_file

    source = tmp_path / "source.txt"
    source.write_text("source", encoding="utf-8")

    class FakeConverter:
        def convert(self, path: Path) -> str:
            assert path == source.resolve()
            return "# Converted\n"

    result = convert_file(source, tmp_path / "converted" / "source.md", FakeConverter())
    assert result.output_path.read_text(encoding="utf-8") == "# Converted\n"
    assert source.read_text(encoding="utf-8") == "source"
