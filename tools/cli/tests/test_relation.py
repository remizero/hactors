from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.project import create_project
from hactors_cli.core.relation import RelationError, relate
from hactors_cli.core.task import create_task

ACTIONS = [
    {
        "id": "AC-00001",
        "type": "implementation",
        "status": "pending",
        "actor": "agent",
        "depends_on": [],
        "deliverable": "",
        "evidence": [],
    }
]


def invoke(root, *args, expected=0):
    result = CliRunner().invoke(cli, [*args, "--root", str(root)])
    assert result.exit_code == expected, result.output
    assert "Traceback" not in result.output
    return result


def manifest_data(project: Path) -> dict:
    return yaml.safe_load((project / "manifest.yaml").read_text())


def write_relations(project: Path, relations) -> None:
    data = manifest_data(project)
    data["relations"] = relations
    (project / "manifest.yaml").write_text(yaml.dump(data, sort_keys=False))


def bump_counter(project: Path, counter: str, identity: str) -> None:
    """Un auxiliar de fixture consume el contador que la CLI consumiría al crear el artefacto."""
    path = project / "manifest.yaml"
    data = yaml.safe_load(path.read_text())
    counters = data.setdefault("counters", {})
    counters[counter] = max(counters.get(counter, 0), int(identity.rsplit("-", 1)[-1]))
    path.write_text(yaml.dump(data, sort_keys=False))


def rfc_document(project: Path, name: str = "RFC-A00001", **extra) -> Path:
    data = {"rfc": name, **extra}
    path = project / "rfcs" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Documento\n\n```yaml\n{yaml.dump(data, sort_keys=False)}```\n")
    for action in extra.get("actions") or []:
        bump_counter(project, "action", action["id"])
    return path


def edge(source: str, target: str, relation: str) -> dict:
    return {"source": source, "target": target, "relation": relation}


@pytest.fixture
def project(hactors_root):
    created = create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", created.name)
    return created


@pytest.fixture
def task(hactors_root, project):
    task_id, _ = create_task(hactors_root, project.name)
    return task_id


def test_relate_appends_the_edge(hactors_root, project, task):
    manifest = relate(hactors_root, project.name, "RFC-A00001", task, "depends-on")
    assert manifest == project / "manifest.yaml"
    assert manifest_data(project)["relations"] == [edge("RFC-A00001", task, "depends-on")]


def test_relate_appends_after_the_recorded_edges(hactors_root, project, task):
    write_relations(project, [edge(task, "RFC-A00001", "informs")])
    relate(hactors_root, project.name, "RFC-A00001", task, "depends-on")
    assert manifest_data(project)["relations"] == [
        edge(task, "RFC-A00001", "informs"),
        edge("RFC-A00001", task, "depends-on"),
    ]


def test_relate_creates_the_list_when_the_manifest_omits_it(hactors_root, project, task):
    data = manifest_data(project)
    del data["relations"]
    (project / "manifest.yaml").write_text(yaml.dump(data, sort_keys=False))
    relate(hactors_root, project.name, "RFC-A00001", task, "depends-on")
    assert manifest_data(project)["relations"] == [edge("RFC-A00001", task, "depends-on")]


def test_relate_preserves_the_other_manifest_fields(hactors_root, project, task):
    relate(hactors_root, project.name, "RFC-A00001", task, "depends-on")
    data = manifest_data(project)
    assert data["project"] == project.name
    assert data["counters"]["task"] == 1
    assert data["counters"]["workflow_run"] == 0


def test_relate_rejects_a_target_that_does_not_resolve(hactors_root, project, task):
    with pytest.raises(RelationError) as excinfo:
        relate(hactors_root, project.name, "RFC-A00001", "RFC-A00009", "depends-on")
    assert "`target` 'RFC-A00009' no resuelve a ningún artefacto del proyecto." in str(excinfo.value)
    assert manifest_data(project)["relations"] == []


def test_relate_rejects_an_unpublished_harness_version(hactors_root, project, task):
    with pytest.raises(RelationError) as excinfo:
        relate(hactors_root, project.name, "RFC-A00001", "HRN-00001@v001", "uses")
    assert "harnesses/HRN-00001/versions/v001/harness.yaml" in str(excinfo.value)


def test_relate_accepts_a_fragment_without_resolving_it(hactors_root, project, task):
    rfc_document(project)
    relate(hactors_root, project.name, task, "RFC-A00001#C1", "informs")
    assert manifest_data(project)["relations"] == [edge(task, "RFC-A00001#C1", "informs")]


def test_relate_accepts_a_target_outside_the_defined_families(hactors_root, project, task):
    relate(hactors_root, project.name, "mi_modulo/servicio", task, "informs")
    assert manifest_data(project)["relations"] == [edge("mi_modulo/servicio", task, "informs")]


def test_relate_does_not_resolve_the_source(hactors_root, project, task):
    relate(hactors_root, project.name, "RFC-A00009", task, "depends-on")
    assert manifest_data(project)["relations"] == [edge("RFC-A00009", task, "depends-on")]


def test_relate_rejects_a_duplicate_edge(hactors_root, project, task):
    relate(hactors_root, project.name, "RFC-A00001", task, "depends-on")
    with pytest.raises(RelationError) as excinfo:
        relate(hactors_root, project.name, "RFC-A00001", task, "depends-on")
    assert "ya consta en relations[1]" in str(excinfo.value)
    assert len(manifest_data(project)["relations"]) == 1


def test_relate_rejects_a_relations_field_that_is_not_a_list(hactors_root, project, task):
    write_relations(project, {"source": task})
    with pytest.raises(RelationError) as excinfo:
        relate(hactors_root, project.name, "RFC-A00001", task, "depends-on")
    assert "`relations` debe ser una lista, no dict." in str(excinfo.value)


@pytest.mark.parametrize("field", ["source", "target", "relation"])
def test_relate_rejects_an_empty_field(hactors_root, project, task, field):
    values = {"source": "RFC-A00001", "target": task, "relation": "depends-on"}
    values[field] = "  "
    with pytest.raises(RelationError) as excinfo:
        relate(hactors_root, project.name, **values)
    assert f"`{field}` requiere un valor no vacío." in str(excinfo.value)
    assert manifest_data(project)["relations"] == []


def test_relate_requires_an_active_project(hactors_root):
    result = invoke(
        hactors_root,
        "relate",
        "--source", "A",
        "--target", "B",
        "--relation", "informs",
        expected=1,
    )
    assert "No hay proyecto activo." in result.output


def test_command_registers_the_edge(hactors_root, project, task):
    result = invoke(
        hactors_root,
        "relate",
        "--source", "RFC-A00001",
        "--target", task,
        "--relation", "depends-on",
    )
    assert "Relación registrada en:" in result.output
    assert manifest_data(project)["relations"] == [edge("RFC-A00001", task, "depends-on")]


def test_command_reports_a_broken_target(hactors_root, project):
    result = invoke(
        hactors_root,
        "relate",
        "--source", "RFC-A00001",
        "--target", "RFC-A00009",
        "--relation", "depends-on",
        expected=1,
    )
    assert "Error: " in result.output
    assert manifest_data(project)["relations"] == []


def test_command_requires_the_three_fields(hactors_root, project):
    invoke(hactors_root, "relate", "--source", "RFC-A00001", "--target", "TASK-00001", expected=2)


def test_the_registered_edge_silences_the_completeness_check(hactors_root, project, task):
    rfc_document(project, depends_on=[task], actions=ACTIONS)
    before = invoke(hactors_root, "validate", expected=1)
    assert "que no consta en `relations` del manifest." in before.output

    invoke(
        hactors_root,
        "relate",
        "--source", "RFC-A00001",
        "--target", task,
        "--relation", "depends-on",
    )
    after = invoke(hactors_root, "validate")
    assert "sin inconsistencias" in after.output
