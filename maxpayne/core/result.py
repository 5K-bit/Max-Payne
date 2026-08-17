"""Structured diagnostic result types."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal

Status = Literal["PASS", "WARN", "FAIL"]
Severity = Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
Risk = Literal["NONE", "LOW", "MEDIUM", "HIGH"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class CheckResult:
    """A single diagnostic check outcome with machine-readable metadata."""

    name: str
    status: Status
    message: str
    suggestion: str
    details: str | None = None
    component: str | None = None
    severity: Severity = "INFO"
    observed_at: str = field(default_factory=_utc_now)
    duration_ms: float | None = None
    evidence: dict[str, object] = field(default_factory=dict)
    remediation_id: str | None = None
    auto_fixable: bool = False
    risk: Risk = "NONE"

    def __post_init__(self) -> None:
        if self.component is None:
            self.component = self.name.split(".", 1)[0]
        if self.severity == "INFO":
            if self.status == "WARN":
                self.severity = "MEDIUM"
            elif self.status == "FAIL":
                self.severity = "HIGH"

    @property
    def check_id(self) -> str:
        """Stable identifier used by APIs and persistence."""
        return self.name

    def to_dict(self, *, lowercase_status: bool = False) -> dict[str, object]:
        payload = asdict(self)
        payload["check_id"] = self.check_id
        if lowercase_status:
            payload["status"] = self.status.lower()
        return payload
