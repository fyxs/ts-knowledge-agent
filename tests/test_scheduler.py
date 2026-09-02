from ts_knowledge_agent.config import Settings, parse_interval_minutes
from ts_knowledge_agent.services.pipeline import RunSummary
from ts_knowledge_agent.services.scheduler import run_scheduler
from pathlib import Path


def test_interval_defaults_to_one_hour():
    assert parse_interval_minutes(None) == 60


def test_interval_accepts_exact_minutes():
    assert parse_interval_minutes("7") == 7


def test_interval_rejects_invalid_values():
    import pytest
    with pytest.raises(ValueError):
        parse_interval_minutes("0")
    with pytest.raises(ValueError):
        parse_interval_minutes("hour")


def test_scheduler_waits_configured_minutes():
    settings = Settings("wanghm", Path("."), Path("."), Path("."), 7)
    calls = []
    sleeps = []
    result = run_scheduler(
        settings,
        lambda _: (calls.append(1) or RunSummary(1, 1, 0, 0)),
        sleeps.append,
        max_runs=2,
    )
    assert result == 0
    assert len(calls) == 2
    assert sleeps == [420]
