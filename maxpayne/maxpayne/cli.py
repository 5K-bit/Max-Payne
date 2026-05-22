"""Typer CLI entrypoint for MaxPayne."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
import logging
from pathlib import Path

import typer

from maxpayne.core.runner import CheckRunner
from maxpayne.ui.console import render_results_table, render_summary, summary_counts

app = typer.Typer(help="MaxPayne - local developer environment doctor.")
doctor_app = typer.Typer(help="Run a focused check group.")
app.add_typer(doctor_app, name="doctor")

logger = logging.getLogger(__name__)


@app.callback()
def app_callback(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging output."),
) -> None:
    """Configure global CLI options."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(levelname)s: %(message)s",
        force=True,
    )
    logger.debug("Debug logging enabled")


@app.command()
def diagnose() -> None:
    """Run all diagnostics."""
    runner = CheckRunner()
    results = runner.run_all()
    render_results_table(results, title="MaxPayne Diagnose")
    render_summary(results)


@app.command()
def ports() -> None:
    """Inspect common local development ports."""
    runner = CheckRunner()
    results = runner.run_group("ports")
    render_results_table(results, title="MaxPayne Ports")
    render_summary(results)


@app.command()
def report(
    output: Path = typer.Option(
        Path("maxpayne-report.json"),
        "--output",
        "-o",
        help="Path for exported JSON report.",
    ),
) -> None:
    """Run all checks and export a JSON diagnostic report."""
    runner = CheckRunner()
    results = runner.run_all()
    pass_count, warn_count, fail_count = summary_counts(results)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {"pass": pass_count, "warn": warn_count, "fail": fail_count},
        "results": [asdict(result) for result in results],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    render_results_table(results, title="MaxPayne Report")
    render_summary(results)
    typer.echo(f"Report written to {output}")


@doctor_app.command("python")
def doctor_python() -> None:
    """Run Python-specific checks."""
    _run_single_group("python", "MaxPayne Doctor: Python")


@doctor_app.command("git")
def doctor_git() -> None:
    """Run Git-specific checks."""
    _run_single_group("git", "MaxPayne Doctor: Git")


@doctor_app.command("docker")
def doctor_docker() -> None:
    """Run Docker-specific checks."""
    _run_single_group("docker", "MaxPayne Doctor: Docker")


@doctor_app.command("ollama")
def doctor_ollama() -> None:
    """Run Ollama-specific checks."""
    _run_single_group("ollama", "MaxPayne Doctor: Ollama")


def _run_single_group(group_name: str, title: str) -> None:
    runner = CheckRunner()
    results = runner.run_group(group_name)
    render_results_table(results, title=title)
    render_summary(results)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
