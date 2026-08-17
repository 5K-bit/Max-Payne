"""Stable OBEOS-facing health adapter and aggregation boundary."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Mapping, Any

from maxpayne.core.engine import MaxPayneEngine
from maxpayne.integrations.events import publish_event

HEALTH_CONTRACT_VERSION = "1.0"
_HEALTH_STATES = {"ok", "degraded", "down", "unknown"}


def _normalize_status(value: object) -> str:
    raw = str(value or "unknown").lower()
    aliases = {
        "healthy": "ok", "pass": "ok", "up": "ok",
        "warn": "degraded", "warning": "degraded",
        "fail": "down", "failed": "down", "error": "down",
    }
    normalized = aliases.get(raw, raw)
    return normalized if normalized in _HEALTH_STATES else "unknown"


def _health_record(payload: Mapping[str, Any], *, fallback_name: str) -> dict[str, object]:
    return {
        "contract_version": HEALTH_CONTRACT_VERSION,
        "name": str(payload.get("name") or payload.get("service") or fallback_name),
        "version": str(payload.get("version") or "unknown"),
        "status": _normalize_status(payload.get("status") or payload.get("overall_status")),
        "node": str(payload.get("node") or "unknown"),
        "checked_at": str(payload.get("checked_at") or payload.get("generated_at") or datetime.now(timezone.utc).isoformat()),
        "dependencies": dict(payload.get("dependencies") or {}),
        "warnings": list(payload.get("warnings") or []),
        "details": dict(payload.get("details") or {}),
    }


class OBEOSHealthAdapter:
    """MaxPayne is the OBEOS health aggregation/remediation authority."""

    def __init__(self, engine: MaxPayneEngine | None = None) -> None:
        self.engine = engine or MaxPayneEngine()

    def snapshot(self, *, record: bool = True, publish: bool = True) -> dict[str, object]:
        report = self.engine.diagnose(profile="obeos", record=record)
        payload = report.to_dict(lowercase_status=True)
        findings = [row for row in payload["results"] if row["status"] in {"warn", "fail"}]
        status = _normalize_status(payload["overall_status"])
        health = {
            "contract_version": HEALTH_CONTRACT_VERSION,
            "name": "maxpayne",
            "version": "0.2.0",
            "status": status,
            "node": payload["node"],
            "checked_at": payload["generated_at"],
            "dependencies": {},
            "warnings": [str(row.get("message") or row.get("name") or "diagnostic finding") for row in findings],
            "details": {"scan_id": payload["scan_id"], "summary": payload["summary"], "findings": findings},
        }
        if publish:
            publish_event("maxpayne.health.snapshot", health)
            publish_event(f"system.health.{status}", health)
        return health

    def aggregate(
        self,
        component_payloads: Iterable[Mapping[str, Any]],
        *,
        include_maxpayne: bool = True,
        record: bool = True,
        publish: bool = True,
    ) -> dict[str, object]:
        records: list[dict[str, object]] = []
        if include_maxpayne:
            records.append(self.snapshot(record=record, publish=publish))
        for index, payload in enumerate(component_payloads):
            records.append(_health_record(payload, fallback_name=f"component-{index + 1}"))
        statuses = {str(item["status"]) for item in records}
        overall = "unknown" if not records else "down" if "down" in statuses else "degraded" if ("degraded" in statuses or "unknown" in statuses) else "ok"
        health = {
            "contract_version": HEALTH_CONTRACT_VERSION,
            "name": "obeos",
            "version": "0.9",
            "status": overall,
            "node": str(records[0].get("node") if records else "unknown"),
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "dependencies": {str(item["name"]): str(item["status"]) for item in records},
            "warnings": [warning for item in records for warning in list(item.get("warnings") or [])],
            "details": {"components": records},
        }
        if publish:
            publish_event("maxpayne.health.aggregate", health)
            publish_event(f"system.health.{overall}", health)
        return health
