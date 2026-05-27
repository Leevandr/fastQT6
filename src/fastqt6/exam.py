"""Demo exam templates bundled with fastqt6."""

from __future__ import annotations

import shutil
import tempfile
import urllib.request
import zipfile
from importlib.resources import files
from pathlib import Path

TEMPLATE_RESOURCE = "templates/demo_exam_obuv"
GUIDE_RESOURCE = "docs/DEMO_EXAM_OBUV.md"
DEMO_28_REPO_URL = "https://github.com/yulechkamsk1/demo_28"
DEMO_28_ARCHIVE_URL = f"{DEMO_28_REPO_URL}/archive/refs/heads/master.zip"


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


def scaffold_demo_28(target_dir: str | Path, force: bool = False) -> Path:
    """Download and create the public demo_28 PyQt6/MySQL variant."""

    target = Path(target_dir)
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(
            f"{target} is not empty. Use --force to copy the template over existing files."
        )

    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive_path = Path(tmp) / "demo_28.zip"
        urllib.request.urlretrieve(DEMO_28_ARCHIVE_URL, archive_path)
        extract_dir = Path(tmp) / "extract"
        extract_dir.mkdir()
        _extract_zip_safely(archive_path, extract_dir)

        roots = [path for path in extract_dir.iterdir() if path.is_dir()]
        if not roots:
            raise RuntimeError("Downloaded archive does not contain a project directory.")

        _copy_path_tree(roots[0], target)

    _write_demo_28_helpers(target)
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


def _copy_path_tree(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        destination = target / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, destination)


def _extract_zip_safely(archive_path: Path, target: Path) -> None:
    target_root = target.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            destination = (target / member.filename).resolve()
            if not str(destination).startswith(str(target_root)):
                raise RuntimeError(f"Unsafe path in downloaded archive: {member.filename}")
        archive.extractall(target)


def _write_demo_28_helpers(target: Path) -> None:
    requirements = target / "requirements.txt"
    if not requirements.exists():
        requirements.write_text("PyQt6\nPyMySQL\n", encoding="utf-8")

    gitignore = target / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            ".venv/\n.idea/\n__pycache__/\n*.py[cod]\n.pytest_cache/\ndist/\nbuild/\n",
            encoding="utf-8",
        )

    readme = target / "FASTQT6_README.md"
    readme.write_text(
        "# demo_28 variant\n\n"
        f"Source repository: {DEMO_28_REPO_URL}\n\n"
        "This project is downloaded from the public GitHub repository when you run "
        "`fastqt6 demo-28`. The original repository does not include a license file, "
        "so check permissions before redistributing the source code.\n\n"
        "## Run\n\n"
        "```powershell\n"
        "python -m pip install -r requirements.txt\n"
        "python -m authwindow\n"
        "```\n\n"
        "## Database\n\n"
        "Import `shoes (1).sql` into MySQL. The connection is configured in "
        "`database/db.py`: database `shoes`, host `localhost`, port `3307`, "
        "user `root`, password `root`.\n",
        encoding="utf-8",
    )
