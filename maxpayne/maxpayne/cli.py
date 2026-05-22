"""Typer CLI entrypoint for MaxPayne."""

import typer

from maxpayne.core.runner import CheckRunner
from maxpayne.ui.console import render_results_table, render_summary

app = typer.Typer(help="MaxPayne - local developer environment doctor.")
doctor_app = typer.Typer(help="Run a focused check group.")
app.add_typer(doctor_app, name="doctor")


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
