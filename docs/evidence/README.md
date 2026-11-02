# Acceptance evidence for 0.2.0

| File | What it is |
| --- | --- |
| `maxpayne-live.txt` | Commands, exit codes and output from a live run on a Linux machine (Python 3.13): profiles, diagnose, history, report, bad-profile error, remediation gates, dashboard, service probes, wheel build and clean-venv install. |
| `test-run.txt` | `pytest -q` result for the tested tree. |
| `wheel-build-sha256.txt` | SHA-256 of the wheel and sdist built during acceptance. The published release carries its own `SHA256SUMS` from the release workflow; they can differ because build metadata changes with the build environment. |

Scope: automated tests and local runtime on Linux only. Not covered: live Windows host, a soak run, and applying a mutating remediation to a real machine.
