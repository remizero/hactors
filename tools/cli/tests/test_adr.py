from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.adr import NAME_SEPARATOR, AdrError, create_adr, descriptive_name
from hactors_cli.core.project import create_project

SPECS = Path(__file__).resolve().parents[3] / "specs"
TEMPLATE_DEFAULTS = {"adr": "", "title": "", "status": "proposed", "date": ""}


def invoke(root, *args, expected=0):
    result = CliRunner().invoke(cli, [*args, "--root", str(root)])
    assert result.exit_code == expected, result.output
    assert "Traceback" not in result.output
    return result


def counters(project: Path) -> dict:
    return yaml.safe_load((project / "manifest.yaml").read_text())["counters"]


def set_counter(project: Path, name: str, value: int) -> None:
    manifest = project / "manifest.yaml"
    data = yaml.safe_load(manifest.read_text())
    data["counters"][name] = value
    manifest.write_text(yaml.dump(data, sort_keys=False))


def front_matter(path: Path) -> dict:
    text = path.read_text()
    assert text.startswith("---\n")
    return yaml.safe_load(text[len("---\n") :].split("\n---\n", 1)[0])


@pytest.fixture
def project(hactors_root):
    created = create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", created.name)
    return created


def test_create_adr_writes_the_template_header(hactors_root, project):
    adr_id, path = create_adr(hactors_root, project.name, "Formato binario de los registros")
    assert adr_id == "ADR-00001"
    assert path == project / "decisions" / f"ADR-00001{NAME_SEPARATOR}formato-binario-de-los-registros.md"
    assert front_matter(path) == {**TEMPLATE_DEFAULTS, "adr": adr_id, "title": "Formato binario de los registros"}
    assert "Estructura y secciones: `specs/templates/ADR_TEMPLATE.md`." in path.read_text()


def test_the_separator_is_the_one_decisions_md_fixes():
    text = (SPECS / "DECISIONS.md").read_text()
    assert f"decisions/ADR-nnnnn{NAME_SEPARATOR}nombre-descriptivo.md" in text


def test_the_header_fields_match_the_template_document():
    document = (SPECS / "templates" / "ADR_TEMPLATE.md").read_text()
    table = document.split("## Cabecera\n", 1)[1].split("\n## ", 1)[0]
    documented = {line.split("|")[1].strip().strip("`") for line in table.splitlines() if line.startswith("| `")}
    assert documented == set(TEMPLATE_DEFAULTS)
    assert yaml.safe_load((SPECS / "templates" / "adr_template.yaml").read_text()) == TEMPLATE_DEFAULTS


def test_create_adr_registers_the_declared_values(hactors_root, project):
    _, path = create_adr(hactors_root, project.name, "Una decisión", status="accepted", date="2026-10-31")
    assert front_matter(path) == {
        "adr": "ADR-00001", "title": "Una decisión", "status": "accepted", "date": "2026-10-31",
    }


def test_create_adr_consumes_the_counter(hactors_root, project):
    create_adr(hactors_root, project.name, "La primera")
    set_counter(project, "adr", 7)
    adr_id, path = create_adr(hactors_root, project.name, "La segunda")
    assert adr_id == "ADR-00008"
    assert counters(project)["adr"] == 8
    assert path.is_file()


def test_create_adr_keeps_one_file_per_decision(hactors_root, project):
    create_adr(hactors_root, project.name, "La primera")
    _, second = create_adr(hactors_root, project.name, "La segunda")
    assert sorted(path.name for path in (project / "decisions").iterdir()) == [
        f"ADR-00001{NAME_SEPARATOR}la-primera.md",
        second.name,
    ]


def test_create_adr_rejects_an_existing_file_without_consuming_the_counter(hactors_root, project):
    target = project / "decisions" / f"ADR-00001{NAME_SEPARATOR}la-decisión.md"
    target.write_text("# Ocupado\n")
    with pytest.raises(AdrError) as excinfo:
        create_adr(hactors_root, project.name, "La decisión")
    assert "Ya existe una decisión en" in str(excinfo.value)
    assert counters(project)["adr"] == 0


@pytest.mark.parametrize("title", ["???", "   ", "—"])
def test_create_adr_rejects_a_title_without_a_descriptive_name(hactors_root, project, title):
    with pytest.raises(AdrError, match="no produce un nombre descriptivo"):
        create_adr(hactors_root, project.name, title)
    assert counters(project)["adr"] == 0


def test_create_adr_requires_the_decisions_directory(hactors_root, project):
    (project / "decisions").rmdir()
    with pytest.raises(AdrError, match="El directorio 'decisions/' del proyecto no existe."):
        create_adr(hactors_root, project.name, "Una decisión")


@pytest.mark.parametrize(
    "title, name",
    [
        ("Formato binario", "formato-binario"),
        ("  Espacios  repetidos ", "espacios-repetidos"),
        ("Decisión con acentos y ñ", "decisión-con-acentos-y-ñ"),
        ("Puntuación: comas, puntos.", "puntuación-comas-puntos"),
        ("sub_raya", "sub_raya"),
    ],
)
def test_descriptive_name(title, name):
    assert descriptive_name(title) == name


def test_command_creates_the_decision(hactors_root, project):
    result = invoke(hactors_root, "create-adr", "--title", "Una decisión registrada")
    assert "Decisión ADR-00001 creada en:" in result.output
    assert (project / "decisions" / f"ADR-00001{NAME_SEPARATOR}una-decisión-registrada.md").is_file()


def test_command_requires_the_title(hactors_root, project):
    invoke(hactors_root, "create-adr", expected=2)


def test_command_requires_an_active_project(hactors_root):
    result = invoke(hactors_root, "create-adr", "--title", "Una decisión", expected=1)
    assert "No hay proyecto activo." in result.output


def test_the_created_adr_resolves_as_a_relation_target(hactors_root, project):
    create_adr(hactors_root, project.name, "Una decisión")
    invoke(hactors_root, "relate", "--source", "docs/nota.md", "--target", "ADR-00001", "--relation", "informs")
    relations = yaml.safe_load((project / "manifest.yaml").read_text())["relations"]
    assert relations == [{"source": "docs/nota.md", "target": "ADR-00001", "relation": "informs"}]
