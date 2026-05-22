"""Node.js and npm checks."""

import shutil

from maxpayne.core.result import CheckResult


def run_node_checks() -> list[CheckResult]:
    node_available = shutil.which("node") is not None
    npm_available = shutil.which("npm") is not None

    return [
        CheckResult(
            name="node.available",
            status="PASS" if node_available else "FAIL",
            message="node is available." if node_available else "node was not found in PATH.",
            suggestion=(
                "No action required."
                if node_available
                else "Install Node.js and ensure `node` is available in your PATH."
            ),
        ),
        CheckResult(
            name="node.npm",
            status="PASS" if npm_available else "FAIL",
            message="npm is available." if npm_available else "npm was not found in PATH.",
            suggestion=(
                "No action required."
                if npm_available
                else "Install npm and ensure it is available in your PATH."
            ),
        ),
    ]
