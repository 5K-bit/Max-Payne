"""Check orchestration logic."""

from collections.abc import Callable

from maxpayne.checks.docker_check import run_docker_checks
from maxpayne.checks.env_check import run_env_checks
from maxpayne.checks.git_check import run_git_checks
from maxpayne.checks.node_check import run_node_checks
from maxpayne.checks.ollama_check import run_ollama_checks
from maxpayne.checks.ports_check import run_ports_checks
from maxpayne.checks.python_check import run_python_checks
from maxpayne.core.result import CheckResult

CheckGroup = Callable[[], list[CheckResult]]


class CheckRunner:
    """Runs configured check groups."""

    def __init__(self, checks: dict[str, CheckGroup] | None = None) -> None:
        self._checks: dict[str, CheckGroup] = checks or {
            "python": run_python_checks,
            "git": run_git_checks,
            "node": run_node_checks,
            "docker": run_docker_checks,
            "ollama": run_ollama_checks,
            "ports": run_ports_checks,
            "env": run_env_checks,
        }

    def run_all(self) -> list[CheckResult]:
        return self.run_groups(list(self._checks))

    def run_group(self, group_name: str) -> list[CheckResult]:
        if group_name not in self._checks:
            raise ValueError(f"Unknown check group: {group_name}")
        return self._checks[group_name]()

    def run_groups(self, group_names: list[str]) -> list[CheckResult]:
        results: list[CheckResult] = []
        for group_name in group_names:
            results.extend(self.run_group(group_name))
        return results
