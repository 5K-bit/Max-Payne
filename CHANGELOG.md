# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-11-02

First tagged release. The 0.2 feature set (diagnostic profiles, SQLite scan history,
structured JSON reports, OBEOS service probes, approval-gated remediation, optional
local dashboard/API, explain mode) was already in the source; this release makes it
installable, tested in CI and traceable to a tag.

### Added

- `maxpayne --version` prints `maxpayne <version>`; a test keeps it equal to `pyproject.toml`.
- Release workflow: runs the full CI on the tagged commit, builds the sdist and wheel, installs the wheel in a clean
  environment, smoke-tests the CLI, runs the test suite against the installed wheel and publishes with `SHA256SUMS`.
- `CHANGELOG.md`, `SECURITY.md`, `docs/runbook.md` and `docs/releases/v0.2.0.md`.

### Fixed

- CI on `main` was failing because `tests/test_deadlines_authority.py` imports FastAPI's `TestClient`, which the
  `dev` extra did not install. The `dev` extra now includes `fastapi`, `uvicorn` and `httpx2`.

### Changed

- `ci.yml` is reusable (`workflow_call`) and declares read-only permissions.
