"""Check registry used by the engine and external integrations."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from maxpayne.core.result import CheckResult

CheckGroup = Callable[[], list[CheckResult]]


class CheckRegistry:
    """Mutable registry of named diagnostic check groups."""

    def __init__(self, checks: Mapping[str, CheckGroup] | None = None) -> None:
        self._checks: dict[str, CheckGroup] = dict(checks or {})

    def register(self, name: str, check: CheckGroup, *, replace: bool = False) -> None:
        if not name.strip():
            raise ValueError("Check group name cannot be empty.")
        if name in self._checks and not replace:
            raise ValueError(f"Check group already registered: {name}")
        self._checks[name] = check

    def unregister(self, name: str) -> None:
        self._checks.pop(name, None)

    def get(self, name: str) -> CheckGroup:
        try:
            return self._checks[name]
        except KeyError as exc:
            raise ValueError(f"Unknown check group: {name}") from exc

    def names(self) -> list[str]:
        return list(self._checks)

    def as_dict(self) -> dict[str, CheckGroup]:
        return dict(self._checks)

    def clone(self) -> "CheckRegistry":
        return CheckRegistry(self._checks)


def default_registry() -> CheckRegistry:
    """Build the built-in registry lazily to keep imports isolated."""
    from maxpayne.checks.docker_check import run_docker_checks
    from maxpayne.checks.env_check import run_env_checks
    from maxpayne.checks.git_check import run_git_checks
    from maxpayne.checks.node_check import run_node_checks
    from maxpayne.checks.ollama_check import run_ollama_checks
    from maxpayne.checks.ports_check import run_ports_checks
    from maxpayne.checks.python_check import run_python_checks
    from maxpayne.checks.services_check import run_service_checks
    from maxpayne.checks.windows_check import run_windows_checks

    return CheckRegistry({
        "python": run_python_checks,
        "git": run_git_checks,
        "node": run_node_checks,
        "docker": run_docker_checks,
        "ollama": run_ollama_checks,
        "ports": run_ports_checks,
        "env": run_env_checks,
        "windows": run_windows_checks,
        "services": run_service_checks,
    })
