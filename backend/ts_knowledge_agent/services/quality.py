from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class QualityReport:
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def inspect_markdown(text: str) -> QualityReport:
    errors: list[str] = []
    warnings: list[str] = []
    if not text.strip():
        errors.append("empty markdown output")
    if "\ufffd" in text:
        errors.append("contains Unicode replacement characters")
    if not re.search(r"^#\s+\S+", text, flags=re.MULTILINE):
        warnings.append("no Markdown H1 title detected")
    repeated = re.findall(r"(.)\1{1,}", text)
    if repeated:
        warnings.append(f"contains {len(repeated)} adjacent repeated-character patterns")
    if len(text.strip()) < 80:
        warnings.append("very short markdown output")
    return QualityReport(tuple(errors), tuple(warnings))
