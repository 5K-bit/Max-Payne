"""Git checks."""

import shutil
import subprocess

from maxpayne.core.result import CheckResult


def _read_git_config(key: str) -> str | None:
    command = ["git", "config", "--global", "--get", key]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def run_git_checks() -> list[CheckResult]:
    results: list[CheckResult] = []

    git_available = shutil.which("git") is not None
    results.append(
        CheckResult(
            name="git.available",
            status="PASS" if git_available else "FAIL",
            message="git is available." if git_available else "git was not found in PATH.",
            suggestion=(
                "No action required."
                if git_available
                else "Install git and ensure it is available in your PATH."
            ),
        )
    )

    if not git_available:
        return results

    git_name = _read_git_config("user.name")
    git_email = _read_git_config("user.email")
    identity_configured = bool(git_name and git_email)
    detail = f"user.name={git_name or '<unset>'}, user.email={git_email or '<unset>'}"

    results.append(
        CheckResult(
            name="git.identity",
            status="PASS" if identity_configured else "WARN",
            message=(
                "Global git identity is configured."
                if identity_configured
                else "Global git identity is incomplete."
            ),
            suggestion=(
                "No action required."
                if identity_configured
                else "Run `git config --global user.name \"Your Name\"` and "
                "`git config --global user.email \"you@example.com\"`."
            ),
            details=detail,
        )
    )

    return results
