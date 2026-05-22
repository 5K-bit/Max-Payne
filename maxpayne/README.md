# MaxPayne

MaxPayne is a local developer environment doctor. It diagnoses common setup
problems before they break a project.

## Features

- Diagnose core tooling health in one command
- Check Python, Git, Node, Docker, and Ollama
- Inspect common local ports for conflicts
- Validate common project environment setup files

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
maxpayne doctor python
maxpayne doctor git
maxpayne doctor docker
maxpayne doctor ollama
```

## Development

```bash
pytest
```
