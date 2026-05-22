"""Ollama checks."""

import shutil

import psutil

from maxpayne.core.result import CheckResult

OLLAMA_PORT = 11434


def _is_port_listening(port: int) -> bool:
    for connection in psutil.net_connections(kind="inet"):
        local = connection.laddr
        if not local:
            continue
        if local.port == port and connection.status == psutil.CONN_LISTEN:
            return True
    return False


def run_ollama_checks() -> list[CheckResult]:
    results: list[CheckResult] = []

    ollama_available = shutil.which("ollama") is not None
    results.append(
        CheckResult(
            name="ollama.available",
            status="PASS" if ollama_available else "FAIL",
            message=(
                "ollama CLI is available."
                if ollama_available
                else "ollama CLI was not found in PATH."
            ),
            suggestion=(
                "No action required."
                if ollama_available
                else "Install Ollama and ensure `ollama` is available in your PATH."
            ),
        )
    )

    try:
        server_running = _is_port_listening(OLLAMA_PORT)
        details = None
    except psutil.AccessDenied:
        server_running = False
        details = "Unable to inspect local ports due to permission limits."

    results.append(
        CheckResult(
            name="ollama.server",
            status="PASS" if server_running else "WARN",
            message=(
                f"Ollama server appears to be listening on localhost:{OLLAMA_PORT}."
                if server_running
                else f"Ollama server is not listening on localhost:{OLLAMA_PORT}."
            ),
            suggestion=(
                "No action required."
                if server_running
                else "Start Ollama (`ollama serve`) before running local models."
            ),
            details=details,
        )
    )

    return results
