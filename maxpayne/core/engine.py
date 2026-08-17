"""High-level MaxPayne engine for CLI, API, and OBEOS consumers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import platform
import socket
import time
import uuid

from maxpayne.core.history import HistoryStore
from maxpayne.core.profiles import resolve_profile
from maxpayne.core.result import CheckResult
from maxpayne.core.runner import CheckRunner
from maxpayne.core.system import detect_platform


@dataclass(slots=True)
class DiagnosticReport:
    scan_id: str
    generated_at: str
    profile: str
    platform: dict[str, object]
    node: str
    summary: dict[str, int]
    results: list[CheckResult]
    duration_ms: float

    @property
    def overall_status(self) -> str:
        if self.summary["fail"]:
            return "fail"
        if self.summary["warn"]:
            return "warn"
        return "pass"

    def to_dict(self, *, lowercase_status: bool = True) -> dict[str, object]:
        return {"scan_id": self.scan_id, "generated_at": self.generated_at, "profile": self.profile,
                "platform": dict(self.platform), "node": self.node, "overall_status": self.overall_status,
                "summary": dict(self.summary), "duration_ms": self.duration_ms,
                "results": [result.to_dict(lowercase_status=lowercase_status) for result in self.results]}


class MaxPayneEngine:
    """Stable programmatic interface for MaxPayne diagnostics."""

    def __init__(self, runner: CheckRunner | None = None, history: HistoryStore | None = None) -> None:
        self.runner = runner or CheckRunner()
        self.history = history

    def diagnose(self, *, profile: str = "all", groups: list[str] | None = None, record: bool = True) -> DiagnosticReport:
        if groups is not None and profile != "all":
            raise ValueError("Use a profile or explicit groups, not both.")
        selected = list(groups) if groups is not None else resolve_profile(profile, self.runner.registry.names())
        started = time.perf_counter()
        results = self.runner.run_all() if groups is None and profile == "all" else self.runner.run_groups(selected)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        pass_count = sum(result.status == "PASS" for result in results)
        warn_count = sum(result.status == "WARN" for result in results)
        fail_count = sum(result.status == "FAIL" for result in results)
        system_name, is_wsl = detect_platform()
        report = DiagnosticReport(
            scan_id=str(uuid.uuid4()), generated_at=datetime.now(timezone.utc).isoformat(),
            profile=profile if groups is None else "custom",
            platform={"system": system_name, "is_wsl": is_wsl, "release": platform.release(), "python": platform.python_version()},
            node=socket.gethostname(), summary={"pass": pass_count, "warn": warn_count, "fail": fail_count},
            results=results, duration_ms=duration_ms)
        if record and self.history is not None:
            self.history.record(report.to_dict(lowercase_status=False))
        return report
