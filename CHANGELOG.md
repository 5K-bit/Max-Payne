# Changelog

All notable changes to MaxPayne are documented here.

The project follows semantic versioning while the public API is being stabilized.

## [0.2.0] - 2026-08-16

### Added

- `MaxPayneEngine` as the stable programmatic diagnostics interface.
- Structured diagnostic metadata including component, severity, evidence, timing, remediation identifiers, fixability, and risk.
- Pluggable check registry.
- Diagnostic profiles for `all`, `minimal`, `workstation`, and `obeos` workloads.
- Configurable HTTP service health probes for local and OBEOS services.
- SQLite diagnostic history.
- Default-deny remediation policy with dry-run behavior and explicit approval requirements.
- Additional destructive-action approval for high-risk remediation.
- OBEOS health adapter for consuming MaxPayne without shelling out to the CLI.
- Optional FastAPI interface and local web health console.
- API endpoints for health, diagnosis, history, and remediation requests.

### Changed

- Findings now connect diagnosis to remediation metadata without automatically executing repairs.
- Reporting includes scan identity, host information, duration, and richer machine-readable results.
- MaxPayne's architecture now separates diagnostics, policy, remediation, integrations, and presentation surfaces.
- Existing CLI commands remain compatible with the original workflow.

### Security

- Remediation is no longer treated as an implicit consequence of diagnosis.
- Destructive repair operations require explicit policy permission.
- Service-probe evidence is designed to avoid credential leakage.

## [0.1.0] - 2026-05-22

### Added

- Initial developer-environment diagnostics CLI.
- Python, Git, Node, Docker, Ollama, port, environment, and Windows checks.
- JSON report export.
- Targeted healing commands for Git configuration, environment files, ports, and Python dependencies.
- Local Ollama crash-log explanations with deterministic heuristic fallback.
- GitHub Actions CI.

[0.2.0]: https://github.com/5K-bit/Max-Payne/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/5K-bit/Max-Payne/releases/tag/v0.1.0