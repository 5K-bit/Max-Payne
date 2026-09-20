"""Check orchestration logic."""

from __future__ import annotations

import logging
import time
import threading

from maxpayne.core.registry import CheckGroup, CheckRegistry, default_registry
from maxpayne.core.result import CheckResult

logger = logging.getLogger(__name__)


class CheckRunner:
    """Runs configured check groups with per-group failure containment."""

    def __init__(self, checks: dict[str, CheckGroup] | None = None, registry: CheckRegistry | None = None, *, timeout_seconds: float = 15.0) -> None:
        self.timeout_seconds = max(.01, min(timeout_seconds, 60))
        self._active = {}
        self._lock = threading.Lock()
        self._slots = threading.BoundedSemaphore(4)
        if checks is not None and registry is not None:
            raise ValueError("Provide checks or registry, not both.")
        self._registry = CheckRegistry(checks) if checks is not None else (registry.clone() if registry is not None else default_registry())

    @property
    def registry(self) -> CheckRegistry:
        return self._registry

    def run_all(self) -> list[CheckResult]:
        return self.run_groups(self._registry.names())

    def _run_group(self, group_name: str) -> list[CheckResult]:
        check_group = self._registry.get(group_name)
        started = time.perf_counter()
        try:
            results = check_group()
        except Exception as exc:  # pragma: no cover - broad catch by design
            logger.exception("Check group %s crashed", group_name)
            results = [CheckResult(name=f"{group_name}.runtime", status="FAIL", message=f"{group_name} checks failed unexpectedly.", suggestion="Re-run with --debug and inspect logs.", details=f"{type(exc).__name__}: {exc}", component=group_name, severity="HIGH")]
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        for result in results:
            if result.duration_ms is None:
                result.duration_ms = elapsed_ms
        return results

    def run_group(self, group_name: str, *, timeout_seconds=None) -> list[CheckResult]:
        self._registry.get(group_name)  # Validate before starting a worker.
        wait = self.timeout_seconds if timeout_seconds is None else max(0, timeout_seconds)
        with self._lock:
            active = self._active.get(group_name)
            if active is None:
                if not self._slots.acquire(blocking=False):
                    return self._timeout(group_name, "Diagnostic worker capacity is full.")
                done, result = threading.Event(), []
                active = (done, result)
                self._active[group_name] = active
                def run():
                    try:
                        result.extend(self._run_group(group_name))
                    finally:
                        done.set()
                        self._slots.release()
                threading.Thread(target=run,name="maxpayne-"+group_name,daemon=True).start()
        done, result = active
        if not done.wait(wait):
            return self._timeout(group_name, "Diagnostic deadline exceeded. Its bounded worker is still finishing; overlapping work is suppressed.")
        with self._lock:
            if self._active.get(group_name) is active:
                self._active.pop(group_name,None)
        return list(result)

    def _timeout(self, group_name, message):
        return [CheckResult(name=f"{group_name}.timeout",status="FAIL",message=message,
            suggestion="Inspect the component connection and retry after it recovers.",component=group_name,severity="HIGH")]

    def run_groups(self, group_names: list[str]) -> list[CheckResult]:
        results = []
        deadline = time.monotonic() + self.timeout_seconds
        for group_name in group_names:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                results.extend(self._timeout(group_name,"Scan deadline exhausted before this group started."))
            else:
                results.extend(self.run_group(group_name,timeout_seconds=remaining))
        return results
