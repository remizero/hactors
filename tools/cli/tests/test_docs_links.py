import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXCLUDED_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__"}
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")

LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
HEADING = re.compile(r"^#{1,6}[ \t]+(.*)$", re.MULTILINE)
PUNCTUATION = re.compile(r"[^\w\s-]", re.UNICODE)
EMPHASIS = re.compile(r"[`*]")


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in REPO_ROOT.rglob("*.md")
        if path.is_file() and not (set(path.parts) & EXCLUDED_PARTS)
    )


def github_slug(heading: str) -> str:
    return PUNCTUATION.sub("", EMPHASIS.sub("", heading).strip().lower()).replace(" ", "-")


def anchors_of(path: Path) -> set[str]:
    return {github_slug(match.group(1)) for match in HEADING.finditer(path.read_text())}


def local_links() -> list[tuple[Path, int, str]]:
    found = []
    for path in markdown_files():
        text = path.read_text()
        for match in LINK.finditer(text):
            target = match.group(2).strip()
            if target.startswith(EXTERNAL_PREFIXES):
                continue
            found.append((path, text[: match.start()].count("\n") + 1, target))
    return found


def broken_links() -> list[str]:
    problems = []
    for path, lineno, target in local_links():
        where = f"{path.relative_to(REPO_ROOT).as_posix()}:{lineno}"
        route, _, fragment = target.partition("#")
        destination = (path.parent / route).resolve() if route else path.resolve()
        if not destination.exists():
            problems.append(f"{where}: destino inexistente -> {target}")
            continue
        if not fragment:
            continue
        if destination.suffix != ".md":
            problems.append(f"{where}: ancla hacia un archivo que no es Markdown -> {target}")
            continue
        slugs = anchors_of(destination)
        if not slugs:
            problems.append(f"{where}: el destino no tiene encabezados que anclar -> {target}")
        elif fragment not in slugs:
            problems.append(f"{where}: ancla inexistente -> {target}")
    return problems


def test_the_scan_covers_the_repository_documentation():
    scanned = {path.relative_to(REPO_ROOT).as_posix() for path in markdown_files()}
    assert {
        "README.md",
        "TODO.md",
        "specs/RFC.md",
        "specs/HACTORS_SYSTEM.md",
        "specs/templates/EVD_TEMPLATE.md",
    } <= scanned, f"faltan documentos conocidos en el barrido: {sorted(scanned)}"
    assert local_links(), "no se encontró ningún enlace local; el barrido no revisa nada"


def test_local_markdown_links_and_anchors_resolve():
    assert broken_links() == []


def test_anchored_links_are_exercised():
    anchored = [target for _, _, target in local_links() if "#" in target]
    assert anchored, "ningún enlace local lleva ancla; la comprobación de anclas no se ejerce"
