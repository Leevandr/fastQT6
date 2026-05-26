"""Demo exam templates bundled with fastqt6."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

TEMPLATE_RESOURCE = "templates/demo_exam_obuv"
GUIDE_RESOURCE = "docs/DEMO_EXAM_OBUV.md"


def scaffold_demo_exam_obuv(target_dir: str | Path, force: bool = False) -> Path:
    """Create a ready PyQt6/MySQL demo exam project for ООО «Обувь»."""

    target = Path(target_dir)
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(
            f"{target} is not empty. Use --force to copy the template over existing files."
        )

    target.mkdir(parents=True, exist_ok=True)
    template = files("fastqt6").joinpath(TEMPLATE_RESOURCE)
    _copy_resource_tree(template, target)
    return target


def demo_exam_guide_path() -> str:
    """Return the installed path to the bundled demo exam guide."""

    return str(files("fastqt6").joinpath(GUIDE_RESOURCE))


def read_demo_exam_guide() -> str:
    """Read the bundled demo exam guide."""

    return files("fastqt6").joinpath(GUIDE_RESOURCE).read_text(encoding="utf-8")


def copy_demo_exam_guide(target: str | Path = "DEMO_EXAM_OBUV.md") -> Path:
    """Copy the bundled demo exam guide into the current project."""

    path = Path(target)
    path.write_text(read_demo_exam_guide(), encoding="utf-8")
    return path


def _copy_resource_tree(resource, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for child in resource.iterdir():
        destination = target / child.name
        if child.is_dir():
            _copy_resource_tree(child, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(child.read_bytes())
