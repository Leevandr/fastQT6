"""Offline tutorial access for installed fastqt6 packages."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

TUTORIAL_RESOURCE = "docs/PYCHARM_TUTORIAL.md"


def tutorial_path() -> str:
    """Return the installed tutorial path shown by PyCharm in site-packages."""

    return str(files("fastqt6").joinpath(TUTORIAL_RESOURCE))


def read_tutorial() -> str:
    """Read the bundled offline tutorial."""

    return files("fastqt6").joinpath(TUTORIAL_RESOURCE).read_text(encoding="utf-8")


def copy_tutorial(target: str | Path = "FASTQT6_TUTORIAL.md") -> Path:
    """Copy the bundled tutorial into the current project."""

    path = Path(target)
    path.write_text(read_tutorial(), encoding="utf-8")
    return path
