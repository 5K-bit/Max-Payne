"""SQLite-backed diagnostic history."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping


class HistoryStore:
    """Persist scan summaries and findings without coupling to the UI."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript("""
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY, generated_at TEXT NOT NULL, profile TEXT NOT NULL,
                platform_json TEXT NOT NULL, node TEXT NOT NULL, pass_count INTEGER NOT NULL,
                warn_count INTEGER NOT NULL, fail_count INTEGER NOT NULL, duration_ms REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id TEXT NOT NULL, check_id TEXT NOT NULL,
                status TEXT NOT NULL, component TEXT, severity TEXT, message TEXT NOT NULL,
                suggestion TEXT NOT NULL, details TEXT, observed_at TEXT, duration_ms REAL,
                evidence_json TEXT NOT NULL, remediation_id TEXT, auto_fixable INTEGER NOT NULL,
                risk TEXT, FOREIGN KEY(scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON findings(scan_id);
            CREATE INDEX IF NOT EXISTS idx_findings_check_id ON findings(check_id);
            """)

    def record(self, report: Mapping[str, Any]) -> None:
        summary = report["summary"]
        with self._connect() as connection:
            connection.execute("""INSERT OR REPLACE INTO scans
                (scan_id, generated_at, profile, platform_json, node, pass_count, warn_count, fail_count, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                report["scan_id"], report["generated_at"], report["profile"],
                json.dumps(report["platform"], sort_keys=True), report["node"],
                int(summary["pass"]), int(summary["warn"]), int(summary["fail"]), float(report["duration_ms"])))
            connection.execute("DELETE FROM findings WHERE scan_id = ?", (report["scan_id"],))
            connection.executemany("""INSERT INTO findings
                (scan_id, check_id, status, component, severity, message, suggestion, details,
                 observed_at, duration_ms, evidence_json, remediation_id, auto_fixable, risk)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", [(
                report["scan_id"], row.get("check_id") or row["name"], row["status"], row.get("component"),
                row.get("severity"), row["message"], row["suggestion"], row.get("details"), row.get("observed_at"),
                row.get("duration_ms"), json.dumps(row.get("evidence") or {}, sort_keys=True), row.get("remediation_id"),
                1 if row.get("auto_fixable") else 0, row.get("risk")) for row in report["results"]])

    def list_scans(self, limit: int = 20) -> list[dict[str, Any]]:
        limit = min(max(int(limit), 1), 200)
        with self._connect() as connection:
            rows = connection.execute("""SELECT scan_id, generated_at, profile, platform_json, node,
                pass_count, warn_count, fail_count, duration_ms FROM scans ORDER BY generated_at DESC LIMIT ?""", (limit,)).fetchall()
        return [{"scan_id": row["scan_id"], "generated_at": row["generated_at"], "profile": row["profile"],
                 "platform": json.loads(row["platform_json"]), "node": row["node"],
                 "summary": {"pass": row["pass_count"], "warn": row["warn_count"], "fail": row["fail_count"]},
                 "duration_ms": row["duration_ms"]} for row in rows]

    def list_findings(self, scan_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("""SELECT check_id, status, component, severity, message, suggestion,
                details, observed_at, duration_ms, evidence_json, remediation_id, auto_fixable, risk
                FROM findings WHERE scan_id = ? ORDER BY id""", (scan_id,)).fetchall()
        return [{"check_id": row["check_id"], "status": row["status"], "component": row["component"],
                 "severity": row["severity"], "message": row["message"], "suggestion": row["suggestion"],
                 "details": row["details"], "observed_at": row["observed_at"], "duration_ms": row["duration_ms"],
                 "evidence": json.loads(row["evidence_json"]), "remediation_id": row["remediation_id"],
                 "auto_fixable": bool(row["auto_fixable"]), "risk": row["risk"]} for row in rows]
