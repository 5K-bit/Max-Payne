"""Python and pip checks."""

import shutil
import sys

from maxpayne.core.result import CheckResult

MIN_PYTHON = (3, 11)


def run_python_checks() -> list[CheckResult]:
    results: list[CheckResult] = []

    version_ok = sys.version_info >= MIN_PYTHON
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    required_version = ".".join(str(part) for part in MIN_PYTHON)
    results.append(
        CheckResult(
            name="python.version",
            status="PASS" if version_ok else "FAIL",
            message=f"Python version is {current_version}.",
            suggestion=(
                "No action required."
                if version_ok
                else f"Upgrade to Python {required_version} or newer."
            ),
        )
    )

    pip_available = shutil.which("pip") is not None or shutil.which("pip3") is not None
    results.append(
        CheckResult(
            name="python.pip",
            status="PASS" if pip_available else "FAIL",
            message="pip is available." if pip_available else "pip was not found in PATH.",
            suggestion=(
                "No action required."
                if pip_available
                else "Install pip and ensure it is available in your PATH."
            ),
        )
    )

    return results
