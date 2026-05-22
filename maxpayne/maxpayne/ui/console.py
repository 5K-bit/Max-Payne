"""Rich console rendering helpers."""

from collections import Counter

from rich.console import Console
from rich.table import Table

from maxpayne.core.result import CheckResult

console = Console()

STATUS_COLORS = {"PASS": "green", "WARN": "yellow", "FAIL": "red"}


def _format_status(status: str) -> str:
    color = STATUS_COLORS.get(status, "white")
    return f"[{color}]{status}[/{color}]"


def render_results_table(results: list[CheckResult], title: str = "MaxPayne Report") -> None:
    table = Table(title=title)
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Message", style="white")
    table.add_column("Suggestion", style="magenta")

    for result in results:
        message = result.message
        if result.details:
            message = f"{message}\n[dim]{result.details}[/dim]"
        table.add_row(result.name, _format_status(result.status), message, result.suggestion)

    console.print(table)


def render_summary(results: list[CheckResult]) -> None:
    counts = Counter(result.status for result in results)
    pass_count = counts.get("PASS", 0)
    warn_count = counts.get("WARN", 0)
    fail_count = counts.get("FAIL", 0)

    console.print(
        f"[bold]Summary:[/bold] "
        f"[green]PASS {pass_count}[/green] | "
        f"[yellow]WARN {warn_count}[/yellow] | "
        f"[red]FAIL {fail_count}[/red]"
    )
