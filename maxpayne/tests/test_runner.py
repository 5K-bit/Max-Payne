from maxpayne.core.result import CheckResult
from maxpayne.core.runner import CheckRunner


def test_runner_runs_all_groups() -> None:
    runner = CheckRunner(
        checks={
            "one": lambda: [
                CheckResult("check.one", "PASS", "ok", "none"),
            ],
            "two": lambda: [
                CheckResult("check.two", "WARN", "warn", "fix later"),
            ],
        }
    )

    results = runner.run_all()

    assert len(results) == 2
    assert [result.name for result in results] == ["check.one", "check.two"]


def test_runner_raises_for_unknown_group() -> None:
    runner = CheckRunner(checks={"one": lambda: []})

    try:
        runner.run_group("missing")
    except ValueError as exc:
        assert "Unknown check group" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing group")
