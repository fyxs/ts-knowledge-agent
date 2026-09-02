from __future__ import annotations

import time
from collections.abc import Callable

from ts_knowledge_agent.config import Settings
from ts_knowledge_agent.services.pipeline import RunSummary, run_once


def run_scheduler(
    settings: Settings,
    run: Callable[[Settings], RunSummary] = run_once,
    sleep: Callable[[float], None] = time.sleep,
    max_runs: int | None = None,
) -> int:
    """Run the ingestion pipeline repeatedly at the configured minute interval."""
    completed = 0
    while max_runs is None or completed < max_runs:
        summary = run(settings)
        completed += 1
        if summary.failed:
            return 1
        if max_runs is None or completed < max_runs:
            sleep(settings.scan_interval_minutes * 60)
    return 0
