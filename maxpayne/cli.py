"""Typer CLI entrypoint for MaxPayne."""

from __future__ import annotations
import json, logging
from pathlib import Path
from rich.panel import Panel
import typer
from maxpayne.core.engine import MaxPayneEngine
from maxpayne.core.history import HistoryStore
from maxpayne.core.profiles import profile_names
from maxpayne.core.remediation import RemediationExecutor, RemediationPolicy
from maxpayne.core.runner import CheckRunner
from maxpayne.explain import explain_file
from maxpayne.heal import apply_default_heal, heal_dependency, heal_env_files, heal_git_config, heal_port
from maxpayne.ui.console import console, render_results_table, render_summary

app = typer.Typer(help="MaxPayne - local developer environment doctor.")
doctor_app = typer.Typer(help="Run a focused check group.")
heal_app = typer.Typer(help="Apply targeted environment fixes.", invoke_without_command=True)
app.add_typer(doctor_app, name="doctor"); app.add_typer(heal_app, name="heal")
logger = logging.getLogger(__name__)


def _default_history_path() -> Path: return Path.home() / ".maxpayne" / "history.db"
def _engine(*, no_history: bool = False) -> MaxPayneEngine: return MaxPayneEngine(history=None if no_history else HistoryStore(_default_history_path()))

@app.callback()
def app_callback(debug: bool = typer.Option(False, "--debug", help="Enable debug logging output.")) -> None:
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, format="%(levelname)s: %(message)s", force=True)

@app.command()
def diagnose(profile: str = typer.Option("all", "--profile", "-p"), no_history: bool = typer.Option(False, "--no-history")) -> None:
    try: report = _engine(no_history=no_history).diagnose(profile=profile)
    except ValueError as exc: raise typer.BadParameter(str(exc)) from exc
    render_results_table(report.results, title=f"MaxPayne Diagnose: {report.profile}"); render_summary(report.results)
    typer.echo(f"scan={report.scan_id} duration_ms={report.duration_ms}")

@app.command()
def ports() -> None:
    results = CheckRunner().run_group("ports"); render_results_table(results, title="MaxPayne Ports"); render_summary(results)

@app.command()
def report(output: Path = typer.Option(Path("maxpayne-report.json"), "--output", "-o"), profile: str = typer.Option("all", "--profile", "-p"), no_history: bool = typer.Option(False, "--no-history")) -> None:
    try: diagnostic = _engine(no_history=no_history).diagnose(profile=profile)
    except ValueError as exc: raise typer.BadParameter(str(exc)) from exc
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(diagnostic.to_dict(lowercase_status=True), indent=2), encoding="utf-8")
    render_results_table(diagnostic.results, title=f"MaxPayne Report: {diagnostic.profile}"); render_summary(diagnostic.results); typer.echo(f"Report written to {output}")

@app.command("profiles")
def profiles_command() -> None:
    for name in profile_names(): typer.echo(name)

@app.command("history")
def history_command(limit: int = typer.Option(10, "--limit", min=1, max=200)) -> None:
    typer.echo(json.dumps(HistoryStore(_default_history_path()).list_scans(limit=limit), indent=2))

@app.command("remediate")
def remediate_command(remediation_id: str = typer.Argument(...), parameters: list[str] = typer.Option([], "--param"), apply: bool = typer.Option(False, "--apply"), approve: bool = typer.Option(False, "--approve"), allow_destructive: bool = typer.Option(False, "--allow-destructive")) -> None:
    parsed: dict[str,str] = {}
    for raw in parameters:
        if "=" not in raw: raise typer.BadParameter(f"Invalid --param value: {raw}; use key=value.")
        key, value = raw.split("=",1)
        if not key.strip(): raise typer.BadParameter("Parameter key cannot be empty.")
        parsed[key.strip()] = value.strip()
    executor = RemediationExecutor(policy=RemediationPolicy(allow_mutating=True, allow_destructive=allow_destructive, require_approval=True))
    try: execution = executor.execute(remediation_id, parameters=parsed, dry_run=not apply, approved=approve)
    except (ValueError, TypeError) as exc: raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps(execution.to_dict(), indent=2))

@app.command()
def explain(log_file: Path = typer.Argument(...), model: str = typer.Option("llama3.2", "--model")) -> None:
    if not log_file.exists(): raise typer.BadParameter(f"File not found: {log_file}")
    explanation = explain_file(log_file, model=model); console.print(Panel(explanation.explanation, title=f"MaxPayne Explain ({explanation.source})", border_style="cyan"))

@app.command()
def serve(host: str = typer.Option("127.0.0.1", "--host"), port: int = typer.Option(8788, "--port", min=1, max=65535)) -> None:
    from maxpayne.server import run_server
    try: run_server(host=host, port=port)
    except RuntimeError as exc: raise typer.BadParameter(str(exc)) from exc


def _run_single_group(group_name: str, title: str) -> None:
    results = CheckRunner().run_group(group_name); render_results_table(results, title=title); render_summary(results)

@doctor_app.command("python")
def doctor_python() -> None: _run_single_group("python", "MaxPayne Doctor: Python")
@doctor_app.command("git")
def doctor_git() -> None: _run_single_group("git", "MaxPayne Doctor: Git")
@doctor_app.command("docker")
def doctor_docker() -> None: _run_single_group("docker", "MaxPayne Doctor: Docker")
@doctor_app.command("ollama")
def doctor_ollama() -> None: _run_single_group("ollama", "MaxPayne Doctor: Ollama")
@doctor_app.command("windows")
def doctor_windows() -> None: _run_single_group("windows", "MaxPayne Doctor: Windows")
@doctor_app.command("services")
def doctor_services() -> None: _run_single_group("services", "MaxPayne Doctor: Services")

@heal_app.callback(invoke_without_command=True)
def heal_default(ctx: typer.Context, interactive: bool = typer.Option(False, "--interactive")) -> None:
    if ctx.invoked_subcommand is None:
        results = apply_default_heal(interactive=interactive); render_results_table(results, title="MaxPayne Heal"); render_summary(results)
@heal_app.command("git")
def heal_git(interactive: bool = typer.Option(False, "--interactive")) -> None:
    result=heal_git_config(interactive=interactive); render_results_table([result], title="MaxPayne Heal: Git"); render_summary([result])
@heal_app.command("env")
def heal_env() -> None:
    result=heal_env_files(); render_results_table([result], title="MaxPayne Heal: Env"); render_summary([result])
@heal_app.command("port")
def heal_port_command(port: int = typer.Argument(...), interactive: bool = typer.Option(False, "--interactive")) -> None:
    result=heal_port(port=port, interactive=interactive); render_results_table([result], title=f"MaxPayne Heal: Port {port}"); render_summary([result])
@heal_app.command("dependency")
def heal_dependency_command(package: str = typer.Argument(...)) -> None:
    result=heal_dependency(package); render_results_table([result], title=f"MaxPayne Heal: Dependency {package}"); render_summary([result])


def main() -> None: app()
if __name__ == "__main__": main()
