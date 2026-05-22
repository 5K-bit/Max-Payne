"""Docker checks."""

import shutil
import subprocess

from maxpayne.core.result import CheckResult


def run_docker_checks() -> list[CheckResult]:
    results: list[CheckResult] = []

    docker_available = shutil.which("docker") is not None
    results.append(
        CheckResult(
            name="docker.available",
            status="PASS" if docker_available else "FAIL",
            message=(
                "docker CLI is available."
                if docker_available
                else "docker CLI was not found in PATH."
            ),
            suggestion=(
                "No action required."
                if docker_available
                else "Install Docker and ensure `docker` is available in your PATH."
            ),
        )
    )

    if not docker_available:
        return results

    daemon_check = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
        check=False,
    )
    daemon_running = daemon_check.returncode == 0
    error_output = (daemon_check.stderr or daemon_check.stdout).strip()

    results.append(
        CheckResult(
            name="docker.daemon",
            status="PASS" if daemon_running else "WARN",
            message=(
                "Docker daemon is running."
                if daemon_running
                else "Docker daemon appears to be unavailable."
            ),
            suggestion=(
                "No action required."
                if daemon_running
                else "Start Docker Desktop/service and run `docker info` again."
            ),
            details=error_output or None,
        )
    )

    return results
