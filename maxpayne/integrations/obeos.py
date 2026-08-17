"""Stable OBEOS-facing adapter for MaxPayne health snapshots."""

from __future__ import annotations
from maxpayne.core.engine import MaxPayneEngine


class OBEOSHealthAdapter:
    """Translate a MaxPayne report into a compact OBEOS service contract."""
    def __init__(self, engine: MaxPayneEngine | None = None) -> None:
        self.engine = engine or MaxPayneEngine()
    def snapshot(self, *, record: bool = True) -> dict[str, object]:
        report = self.engine.diagnose(profile="obeos", record=record); payload = report.to_dict(lowercase_status=True)
        return {"service": "maxpayne", "status": payload["overall_status"], "node": payload["node"],
                "generated_at": payload["generated_at"], "scan_id": payload["scan_id"], "summary": payload["summary"],
                "findings": [row for row in payload["results"] if row["status"] in {"warn", "fail"}]}
