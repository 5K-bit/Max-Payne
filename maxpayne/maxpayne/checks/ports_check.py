"""Port occupancy checks."""

import psutil

from maxpayne.core.result import CheckResult

COMMON_PORTS = [3000, 5000, 8000, 8037, 8080, 11434]


def _list_listening_ports() -> set[int]:
    listening_ports: set[int] = set()
    for connection in psutil.net_connections(kind="inet"):
        local = connection.laddr
        if not local:
            continue
        if connection.status == psutil.CONN_LISTEN:
            listening_ports.add(local.port)
    return listening_ports


def run_ports_checks() -> list[CheckResult]:
    try:
        listening_ports = _list_listening_ports()
        permission_detail = None
    except psutil.AccessDenied:
        listening_ports = set()
        permission_detail = "Unable to inspect all ports due to permission limits."

    results: list[CheckResult] = []
    for port in COMMON_PORTS:
        occupied = port in listening_ports
        results.append(
            CheckResult(
                name=f"ports.{port}",
                status="WARN" if occupied else "PASS",
                message=(
                    f"Port {port} is occupied."
                    if occupied
                    else f"Port {port} is available."
                ),
                suggestion=(
                    "Stop the process using this port or change your app port."
                    if occupied
                    else "No action required."
                ),
                details=permission_detail,
            )
        )

    return results
