# MaxPayne

MaxPayne is a local developer environment doctor. It diagnoses common setup
problems before they break a project.
MaxPayne is tested without requiring Docker, Node, Git, or Ollama to be installed.

## Features

- Diagnose local tooling health in one command
- Check Python, Git, Node, Docker, and Ollama readiness
- Inspect common local ports for conflicts with PID/process details
- Validate common project environment setup files
- Export a JSON report for automation and troubleshooting

## Requirements

- Python 3.11+

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## CLI Usage

```bash
maxpayne diagnose
maxpayne ports
maxpayne report
maxpayne report --output ./artifacts/diag.json

maxpayne doctor python
maxpayne doctor git
maxpayne doctor docker
maxpayne doctor ollama

maxpayne --debug diagnose
```

## Notes

- Subprocess checks are protected with a 3-second timeout.
- A single failed check never stops remaining checks.
- Platform detection supports Linux/Windows and flags WSL when detected.

## Development

```bash
pytest
```
