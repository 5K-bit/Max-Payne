"""Configurable HTTP service health probes."""

from __future__ import annotations

import os
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit, urlunsplit

from maxpayne.core.result import CheckResult


def _safe_url(url: str) -> str:
    parts = urlsplit(url)
    hostname = parts.hostname or ""
    if parts.port:
        hostname = f"{hostname}:{parts.port}"
    return urlunsplit((parts.scheme, hostname, parts.path, parts.query, ""))


def _parse_service_urls(raw: str) -> list[tuple[str, str]]:
    services: list[tuple[str, str]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"Invalid service entry: {item}")
        name, url = item.split("=", 1)
        name, url = name.strip(), url.strip()
        if not name or not url:
            raise ValueError(f"Invalid service entry: {item}")
        if urlsplit(url).scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported service URL scheme for {name}")
        services.append((name, url))
    return services


def _probe_service(name: str, url: str, timeout: float) -> CheckResult:
    safe_url = _safe_url(url)
    started = time.perf_counter()
    request = urllib.request.Request(url, headers={"User-Agent": "MaxPayne/0.2"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = int(response.status)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        healthy = 200 <= status_code < 400
        return CheckResult(name=f"services.{name}", status="PASS" if healthy else "FAIL",
            message=f"{name} service is reachable." if healthy else f"{name} service returned HTTP {status_code}.",
            suggestion="No action required." if healthy else f"Inspect the {name} service and its health endpoint.",
            component=name, severity="INFO" if healthy else "HIGH", duration_ms=elapsed_ms,
            evidence={"url": safe_url, "http_status": status_code})
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return CheckResult(name=f"services.{name}", status="FAIL", message=f"{name} service is unreachable.",
            suggestion=f"Start or repair {name}, then rerun the service probe.", details=str(exc), component=name,
            severity="HIGH", duration_ms=elapsed_ms, evidence={"url": safe_url})


def run_service_checks() -> list[CheckResult]:
    raw = os.environ.get("MAXPAYNE_SERVICE_URLS", "").strip()
    if not raw:
        return [CheckResult(name="services.configuration", status="PASS", message="No external service probes are configured.",
            suggestion="Set MAXPAYNE_SERVICE_URLS when OBEOS or another runtime should be monitored.", component="services")]
    try:
        services = _parse_service_urls(raw)
        timeout = max(0.25, float(os.environ.get("MAXPAYNE_SERVICE_TIMEOUT", "2")))
    except (ValueError, TypeError) as exc:
        return [CheckResult(name="services.configuration", status="WARN", message="Service probe configuration is invalid.",
            suggestion="Fix MAXPAYNE_SERVICE_URLS and rerun diagnostics.", details=str(exc), component="services", severity="MEDIUM")]
    return [_probe_service(name, url, timeout) for name, url in services]
