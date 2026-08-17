"""Check orchestration logic."""

from __future__ import annotations

import logging
import time

from maxpayne.core.registry import CheckGroup, CheckRegistry, default_registry
from maxpayne.core.result import CheckResult

logger = logging.getLogger(__name__)


class CheckRunner:
    """Runs configured check groups with per-group failure containment."""

    def __init__(self, checks: dict[str, CheckGroup] | None = None, registry: CheckRegistry | None = None) -> None:
        if checks is not None and registry is not None:
            raise ValueError("Provide checks or registry, not both.")
        self._registry = CheckRegistry(checks) if checks is not None else (registry.clone() if registry is not None else default_registry())

    @property
    def registry(self) -> CheckRegistry:
        return self._registry

    def run_all(self) -> list[CheckResult]:
        return self.run_groups(self._registry.names())

    def run_group(self, group_name: str) -> list[CheckResult]:
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

    def run_groups(self, group_names: list[str]) -> list[CheckResult]:
        results: list[CheckResult] = []
        for group_name in group_names:
            results.extend(self.run_group(group_name))
        return results
