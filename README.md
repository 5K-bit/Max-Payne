# MaxPayne

[![CI](https://github.com/5K-bit/Max-Payne/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/5K-bit/Max-Payne/actions/workflows/ci.yml)

MaxPayne is a local developer environment health, diagnostics, and recovery engine. It can still be used as a standalone CLI, but the core is now designed to be embedded into systems such as OBEOS.

## What changed in 0.2

MaxPayne now has two layers:

```text
Human / OBEOS / API
        |
    MaxPayneEngine
        |
  Check Registry + Profiles
        |
  Structured Findings
        |
  History + Remediation Policy
```

The CLI is still supported. New consumers should use `MaxPayneEngine` rather than shelling out to CLI commands.

### New capabilities

- richer machine-readable findings: component, severity, timing, evidence, remediation, fixability, and risk
- pluggable check registry instead of a hard-coded runner
- diagnostic profiles: `all`, `minimal`, `workstation`, and `obeos`
- configurable HTTP service probes for OBEOS and other local services
- SQLite diagnostic history
- policy-controlled remediation with dry-run and explicit approval
- stable Python engine API
- OBEOS health adapter
- optional FastAPI service and zero-build visual health console

## Installation

```bash
python -m pip install -e .
maxpayne diagnose
```

For the local dashboard/API:

```bash
python -m pip install -e ".[web]"
maxpayne serve
```

Open `http://127.0.0.1:8788`.

## Diagnostics

```bash
# Preserve original behavior: run every registered check group
maxpayne diagnose

# Focused profiles
maxpayne diagnose --profile minimal
maxpayne diagnose --profile workstation
maxpayne diagnose --profile obeos

# Existing focused doctors
maxpayne doctor python
maxpayne doctor git
maxpayne doctor docker
maxpayne doctor ollama
maxpayne doctor windows
maxpayne doctor services

# Export machine-readable report
maxpayne report --profile workstation --output ./artifacts/maxpayne-report.json
```

## OBEOS service probes

MaxPayne does not hard-code OBEOS ports. OBEOS declares the services it wants MaxPayne to monitor:

**PowerShell**

```powershell
$env:MAXPAYNE_SERVICE_URLS="obeos=http://127.0.0.1:8000/api/health,assistant=http://127.0.0.1:7777/api/health"
maxpayne diagnose --profile obeos
```

**bash**

```bash
export MAXPAYNE_SERVICE_URLS="obeos=http://127.0.0.1:8000/api/health,assistant=http://127.0.0.1:7777/api/health"
maxpayne diagnose --profile obeos
```

Credentials embedded in probe URLs are stripped from diagnostic evidence.

## Safe remediation

The original `maxpayne heal ...` commands remain for direct human operation.

Automation should use the policy layer:

```bash
# Dry-run is the default
maxpayne remediate env.generate_example

# Mutating operation requires explicit apply + approval
maxpayne remediate python.install_dependency --param package=fastapi --apply --approve

# Process termination is destructive and is blocked unless separately enabled
maxpayne remediate port.free --param port=8000 --apply --approve --allow-destructive
```

This prevents an OBEOS agent from silently terminating a process or changing the Python environment.

## History

CLI and API scans are persisted by default to:

```text
~/.maxpayne/history.db
```

```bash
maxpayne history --limit 20
maxpayne diagnose --no-history
```

## Python API

```python
from maxpayne import MaxPayneEngine
from maxpayne.core.history import HistoryStore

engine = MaxPayneEngine(history=HistoryStore("maxpayne.db"))
report = engine.diagnose(profile="workstation")

print(report.overall_status)
print(report.to_dict())
```

## OBEOS adapter

```python
from maxpayne.integrations.obeos import OBEOSHealthAdapter

health = OBEOSHealthAdapter().snapshot()
```

The adapter returns a compact service contract containing MaxPayne status, node, scan ID, summary, and only active warnings/failures.

## HTTP API

With the `web` extra installed:

```bash
maxpayne serve --host 127.0.0.1 --port 8788
```

Endpoints:

- `GET /api/health`
- `POST /api/diagnose?profile=workstation`
- `GET /api/history`
- `POST /api/remediate/{remediation_id}`
- `GET /` visual health console

Bind to localhost by default. If OBEOS needs remote access, put MaxPayne behind the same private networking/authentication boundary used by OBEOS rather than exposing it directly to the public internet.

## Explain mode

```bash
maxpayne explain crash.log
maxpayne explain traceback.txt
```

MaxPayne uses local Ollama when available and falls back to deterministic heuristics when it is not.

## Legacy healing commands

Existing commands remain supported:

```bash
maxpayne heal
maxpayne heal --interactive
maxpayne heal git
maxpayne heal env
maxpayne heal port 8000
maxpayne heal dependency fastapi
```

For autonomous or agent-driven callers, prefer `maxpayne remediate`.

## Development

```bash
python -m pip install -e ".[dev,web]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
