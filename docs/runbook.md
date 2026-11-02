# MaxPayne first-use runbook

## Supported environments

Python 3.11 or newer on Linux, macOS or Windows. CI covers Linux with Python 3.11 and 3.12.
Windows-specific checks are unit-tested but were not run on a live Windows host for 0.2.0.

## Install

```bash
python -m venv .venv && . .venv/bin/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install "maxpayne @ https://github.com/5K-bit/Max-Payne/releases/download/v0.2.0/maxpayne-0.2.0-py3-none-any.whl"
maxpayne --version                                  # expect: maxpayne 0.2.0
```

For the optional dashboard, install with the `web` extra instead:
`python -m pip install "maxpayne[web] @ https://github.com/5K-bit/Max-Payne/releases/download/v0.2.0/maxpayne-0.2.0-py3-none-any.whl"`, then `maxpayne serve` and open http://127.0.0.1:8788.

## First real workflow: document the health of your dev environment

```bash
cd <your OBEOS project folder>
maxpayne diagnose --profile obeos           # table of PASS / WARN / FAIL with a suggestion for each
maxpayne report -o maxpayne-report.json --profile obeos
maxpayne history --limit 5                  # earlier scans from ~/.maxpayne/history.db
```

Expected: a table, a summary line such as `23 pass 2 warn 2 fail`, a `scan=<id>` line, and exit code 0.
Failures are findings, not crashes: a missing tool such as Ollama appears as `FAIL ollama.available`.

To monitor OBEOS services, declare them and rerun the `obeos` profile (an unreachable service is reported as a failure):

```bash
export MAXPAYNE_SERVICE_URLS="obeos=http://127.0.0.1:8000/api/health"      # PowerShell: $env:MAXPAYNE_SERVICE_URLS="..."
maxpayne diagnose --profile obeos
```

## Remediation (always dry-run first)

```bash
maxpayne remediate env.generate_example                 # plans only
maxpayne remediate env.generate_example --apply --approve
```

`port.free` terminates a process and is blocked unless you also pass `--allow-destructive`.

## Common failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| `FAIL ollama.available` | Ollama not installed | Install Ollama or ignore if you do not use it |
| `FAIL env.dependencies_file` | Run outside a project folder | `cd` into the project and rerun |
| `maxpayne serve` says FastAPI is missing | `web` extra not installed | `pip install "maxpayne[web]"` |
| `Unknown profile` (exit 2) | Misspelled profile | `maxpayne profiles` |

## Recovery and rollback

Diagnosis is read-only. Remediations that change files print what they change in the dry run; review it first.
To roll back the tool itself: `pip install maxpayne==<previous>` or `pip uninstall maxpayne`.

## Data and backup

Scan history is a single SQLite file at `~/.maxpayne/history.db`. Copy it to back it up; delete it to reset history.
It is not encrypted.

## Verify the installed version

`maxpayne --version`, or `python -c "import maxpayne; print(maxpayne.__version__)"`.
Checksums for release files are in `SHA256SUMS` on the release page.

## Support

Open an issue at https://github.com/5K-bit/Max-Payne/issues with the output of `maxpayne --version` and the failing command.
