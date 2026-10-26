from pathlib import Path

HACTORS_MARKERS = ("specs/templates", "projects")


def find_hactors_root(start: Path) -> Path:
    current = start.resolve()
    for directory in [current, *current.parents]:
        if all((directory / marker).exists() for marker in HACTORS_MARKERS):
            return directory
    return current


def project_dir(root: Path, name: str) -> Path:
    return root / "projects" / name
