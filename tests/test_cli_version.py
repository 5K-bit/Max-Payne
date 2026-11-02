"""The installed CLI must report the same version as the package metadata."""

import tomllib
from pathlib import Path

from typer.testing import CliRunner

from maxpayne import __version__, cli

runner = CliRunner()


def test_version_flag_prints_package_version() -> None:
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == f"maxpayne {__version__}"


def test_source_version_matches_pyproject() -> None:
    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == __version__
