from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

CONVERTER_VERSION = "markitdown"


class Converter(Protocol):
    def convert(self, source: Path) -> str: ...


class MarkItDownConverter:
    def __init__(self) -> None:
        try:
            from markitdown import MarkItDown
        except ImportError as exc:
            raise RuntimeError("MarkItDown is not installed in the active environment") from exc
        self._converter = MarkItDown()

    def convert(self, source: Path) -> str:
        return self._converter.convert(str(source)).text_content


@dataclass(frozen=True)
class ConversionResult:
    source_path: Path
    output_path: Path
    bytes_written: int


def convert_file(source: Path, output: Path, converter: Converter | None = None) -> ConversionResult:
    source = source.expanduser().resolve()
    output = output.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"source file does not exist: {source}")
    if source == output:
        raise ValueError("conversion output must not overwrite the source file")
    output.parent.mkdir(parents=True, exist_ok=True)
    text = (converter or MarkItDownConverter()).convert(source)
    output.write_text(text, encoding="utf-8")
    return ConversionResult(source, output, output.stat().st_size)
