import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import quote

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.adr import create_adr
from hactors_cli.core.evidence import create_evidence
from hactors_cli.core.finding import create_finding
from hactors_cli.core.model import MODEL_SCHEMA, build_model, root_models, write_model
from hactors_cli.core.project import create_project
from hactors_cli.core.rfc_run import create_rfc_run
from hactors_cli.core.summary import create_summary
from hactors_cli.core.task import create_task
from hactors_cli.core.task_run import create_task_run
from hactors_cli.core.test_run import create_test_run
from hactors_cli.core.validate import validate_project
from hactors_cli.core.view import ViewError, render_views
from hactors_cli.core.workflow import create_workflow

MODEL_FIELDS = [
    "schema", "project", "description", "generated_at",
    "counters", "artifacts", "edges", "runs", "problems",
]
STAMP = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
ACTIONS = [
    {
        "id": "ACT-00001",
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


def write_document(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Documento\n\n```yaml\n{yaml.dump(data, sort_keys=False)}```\n")
    return path


def bump_counter(project: Path, counter: str, identity: str) -> None:
    """Un auxiliar de fixture consume el contador que la CLI consumiría al crear el artefacto."""
    path = project / "manifest.yaml"
    data = yaml.safe_load(path.read_text())
    counters = data.setdefault("counters", {})
    digits = "".join(c for c in identity.rsplit("-", 1)[-1] if c.isdigit())
    if not digits:
        return
    counters[counter] = max(counters.get(counter, 0), int(digits))
    path.write_text(yaml.dump(data, sort_keys=False))


def rfc_counter(identity: str) -> str:
    """El contador de tipo que consume una RFC; vacío si su último segmento no es de tipo."""
    segment = identity.rsplit("-", 1)[-1]
    return f"rfc_{segment[0].lower()}" if segment[1:].isdigit() else ""


def rfc_document(project: Path, name: str = "RFC-A00001", actions=None, **extra) -> Path:
    data = {"rfc": name, **extra}
    if actions is not None:
        data["actions"] = actions
    path = write_document(project / "rfcs" / f"{name}.md", data)
    if rfc_counter(name):
        bump_counter(project, rfc_counter(name), name)
    for action in actions or []:
        bump_counter(project, "action", action["id"])
    return path


def plan_document(
    project: Path, plan_id: str = "PLAN-00001", location: str = "plans", **extra
) -> Path:
    path = write_document(project / location / f"{plan_id}.md", {"id": plan_id, **extra})
    bump_counter(project, "plan", plan_id)
    return path


def verification_document(project: Path, test_id: str = "TEST-00001", **extra) -> Path:
    path = write_document(project / "tests" / f"{test_id}.md", {"id": test_id, **extra})
    bump_counter(project, "test", test_id)
    return path


def harness_catalog(project: Path, harness_id: str = "HRN-00001") -> Path:
    path = project / "harnesses" / harness_id / "manifest.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"id: {harness_id}\n"
        "title: Un arnés\n"
        "current_version: 1\n"
        "versions:\n"
        "  - version: 1\n"
        "    status: ready\n"
        "    content_ref: ''\n"
        "    published: 2026-10-01\n"
        "  - version: 2\n"
        "    status: draft\n"
        "    content_ref: ''\n"
        "    published: null\n"
        "relations: []\n"
    )
    bump_counter(project, "harness", harness_id)
    return path


def manifest_data(project: Path) -> dict:
    return yaml.safe_load((project / "manifest.yaml").read_text())


def write_relations(project: Path, relations) -> None:
    data = manifest_data(project)
    data["relations"] = relations
    (project / "manifest.yaml").write_text(yaml.dump(data, sort_keys=False))


def _body(data: dict) -> dict:
    return next(iter(data.values())) if "identity" not in data else data


def set_identity(manifest: Path, **fields) -> None:
    data = yaml.safe_load(manifest.read_text())
    _body(data)["identity"].update(fields)
    manifest.write_text(yaml.dump(data, sort_keys=False))


def set_state(manifest: Path, block: str, **fields) -> None:
    data = yaml.safe_load(manifest.read_text())
    _body(data)[block].update(fields)
    manifest.write_text(yaml.dump(data, sort_keys=False))


def entry(model: dict, identity: str) -> dict:
    found = [item for item in model["artifacts"] if item["id"] == identity]
    assert len(found) == 1, [item["id"] for item in model["artifacts"]]
    return found[0]


def instance(model: dict, identity: str) -> dict:
    found = [item for item in model["runs"] if item["id"] == identity]
    assert len(found) == 1, [item["id"] for item in model["runs"]]
    return found[0]


def board(project: Path) -> str:
    return (project / "views" / "index.html").read_text()


def viewer(hactors_root: Path) -> str:
    return (hactors_root / "projects" / "views" / "index.html").read_text()


def front_matter_of(path: Path) -> dict:
    return yaml.safe_load(path.read_text().split("---\n")[1])


@pytest.fixture
def project(hactors_root):
    created = create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", created.name)
    return created


@pytest.fixture
def runs(hactors_root, project):
    """workflow_run → task_run → rfc_run → test_run."""
    workflow = create_workflow(hactors_root, project.name)
    task_run = create_task_run(hactors_root, project.name, _relative(project, workflow))
    rfc_run = create_rfc_run(hactors_root, project.name, _relative(project, task_run))
    test_run = create_test_run(hactors_root, project.name, _relative(project, rfc_run))
    return {
        "workflow_run": workflow,
        "task_run": task_run,
        "rfc_run": rfc_run,
        "test_run": test_run,
    }


def _relative(project: Path, path: Path) -> str:
    return path.relative_to(project).as_posix()


@pytest.fixture
def populated(hactors_root, project, runs):
    """Un artefacto de cada familia, sin inconsistencias."""
    create_task(hactors_root, project.name, task="Cerrar la deuda", actor="human")
    rfc_document(
        project,
        title="Resolver el fragmento",
        status="accepted",
        proposed_by="human",
        actions=ACTIONS,
    )
    plan_document(project, location="docs/plans", title="Un plan", status="approved")
    create_adr(hactors_root, project.name, "Una decisión")
    create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md", title="Una evidencia")
    create_finding(
        hactors_root, project.name, "tasks/TASK-00001.md", title="Un hallazgo", severity="low"
    )
    create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md", title="El resultado")
    harness_catalog(project)
    return project


# El modelo de lectura.


def test_model_declares_the_contract(hactors_root, populated):
    model = build_model(hactors_root, populated.name)
    assert list(model) == MODEL_FIELDS
    assert model["schema"] == MODEL_SCHEMA
    assert model["project"] == populated.name


def test_generated_at_is_a_utc_stamp(hactors_root, populated):
    assert STAMP.fullmatch(build_model(hactors_root, populated.name)["generated_at"])


def test_only_generated_at_changes_between_projections(hactors_root, populated):
    first = build_model(hactors_root, populated.name)
    second = build_model(hactors_root, populated.name)
    assert first.pop("generated_at")
    assert second.pop("generated_at")
    assert first == second


def test_description_comes_from_project_yaml(hactors_root, populated):
    data = yaml.safe_load((populated / "project.yaml").read_text())
    data["description"] = "Descripción del proyecto"
    (populated / "project.yaml").write_text(yaml.dump(data, sort_keys=False))
    assert build_model(hactors_root, populated.name)["description"] == "Descripción del proyecto"


def test_a_project_without_description_projects_an_empty_one(hactors_root, populated):
    (populated / "project.yaml").unlink()
    assert build_model(hactors_root, populated.name)["description"] == ""


def test_counters_are_reproduced_without_recalculating(hactors_root, populated):
    data = manifest_data(populated)
    data["counters"]["task"] = 9
    (populated / "manifest.yaml").write_text(yaml.dump(data, sort_keys=False))
    model = build_model(hactors_root, populated.name)
    assert model["counters"]["task"] == 9
    assert len([item for item in model["artifacts"] if item["kind"] == "task"]) == 1


def test_edges_are_projected_literally(hactors_root, populated):
    edge = {"source": "TASK-00001", "target": "RFC-A00001", "relation": "derives", "ajeno": 1}
    write_relations(populated, [edge])
    assert build_model(hactors_root, populated.name)["edges"] == [edge]


def test_problems_reproduce_what_validate_reports(hactors_root, populated, runs):
    set_identity(runs["workflow_run"] / "manifest.yaml", task_ref="TASK-00009")
    model = build_model(hactors_root, populated.name)
    assert model["problems"] == validate_project(hactors_root, populated.name)
    assert "`task_ref` 'TASK-00009' no resuelve a tasks/TASK-00009.md." in model["problems"][0]


def test_a_consistent_project_projects_no_problem(hactors_root, populated):
    assert build_model(hactors_root, populated.name)["problems"] == []


# Artefactos.


def test_task_projects_its_status_and_actor(hactors_root, populated):
    task = entry(build_model(hactors_root, populated.name), "TASK-00001")
    assert task["kind"] == "task"
    assert task["path"] == "tasks/TASK-00001.md"
    assert task["title"] == "Cerrar la deuda"
    assert task["status"] == "draft"
    assert task["actor"] == "human"


def test_rfc_projects_its_status_without_actor(hactors_root, populated):
    rfc = entry(build_model(hactors_root, populated.name), "RFC-A00001")
    assert rfc["kind"] == "rfc"
    assert rfc["title"] == "Resolver el fragmento"
    assert rfc["status"] == "accepted"
    assert rfc["actor"] == ""


def test_actions_nest_under_their_rfc(hactors_root, populated):
    model = build_model(hactors_root, populated.name)
    assert entry(model, "RFC-A00001")["actions"] == [
        {"id": "ACT-00001", "type": "implementation", "status": "pending", "actor": "agent"}
    ]
    assert "ACT-00001" not in [item["id"] for item in model["artifacts"]]


def test_an_rfc_without_actions_projects_an_empty_list(hactors_root, populated):
    rfc_document(populated, name="RFC-A00002", actions=[])
    assert entry(build_model(hactors_root, populated.name), "RFC-A00002")["actions"] == []


@pytest.mark.parametrize("location", ["plans", "docs/plans"])
def test_plans_are_projected_from_both_locations(hactors_root, project, location):
    plan_document(project, location=location, title="Un plan", status="approved")
    plan = entry(build_model(hactors_root, project.name), "PLAN-00001")
    assert plan["kind"] == "plan"
    assert plan["path"] == f"{location}/PLAN-00001.md"
    assert plan["status"] == "approved"
    assert plan["actor"] == ""


def test_adr_projects_its_status(hactors_root, populated):
    adr = entry(build_model(hactors_root, populated.name), "ADR-00001")
    assert adr["kind"] == "adr"
    assert adr["title"] == "Una decisión"
    assert adr["status"] == "proposed"
    assert adr["actor"] == ""


def test_a_summary_is_identified_by_the_artifact_it_summarizes(hactors_root, populated):
    model = build_model(hactors_root, populated.name)
    summaries = [item for item in model["artifacts"] if item["kind"] == "summary"]
    assert len(summaries) == 1
    declared = front_matter_of(populated / summaries[0]["path"])
    assert summaries[0]["id"] == declared["artifact"]
    assert summaries[0]["status"] == declared["status"] == "in-progress"
    assert summaries[0]["path"] == "rfcs/RFC-A00001 - Summary.md"


def test_a_workflow_run_summary_is_projected(hactors_root, populated, runs):
    create_summary(hactors_root, populated.name, _relative(populated, runs["workflow_run"]))
    model = build_model(hactors_root, populated.name)
    paths = [item["path"] for item in model["artifacts"] if item["kind"] == "summary"]
    assert paths == [
        "hactors/workflow_run_00001/SUMMARY.md",
        "rfcs/RFC-A00001 - Summary.md",
    ]


def test_evidence_has_no_status_and_finding_projects_its_state(hactors_root, populated):
    model = build_model(hactors_root, populated.name)
    evidence = entry(model, "EVD-00001")
    assert evidence["kind"] == "evidence"
    assert evidence["path"] == "rfcs/EVD-00001.yaml"
    assert evidence["title"] == "Una evidencia"
    assert evidence["status"] == ""
    finding = entry(model, "FND-00001")
    assert finding["kind"] == "finding"
    assert finding["path"] == "tasks/FND-00001.yaml"
    assert finding["status"] == "open"


def test_harness_versions_nest_in_the_catalog(hactors_root, populated):
    harness = entry(build_model(hactors_root, populated.name), "HRN-00001")
    assert harness["kind"] == "harness"
    assert harness["path"] == "harnesses/HRN-00001/manifest.yaml"
    assert harness["status"] == ""
    assert harness["versions"] == [
        {"version": 1, "status": "ready", "published": "2026-10-01"},
        {"version": 2, "status": "draft", "published": ""},
    ]


def test_a_test_is_projected_like_the_other_documents(hactors_root, populated, runs):
    verification_document(populated)
    set_identity(runs["test_run"] / "manifest.yaml", test_ref="TEST-00001")
    model = build_model(hactors_root, populated.name)
    test = entry(model, "TEST-00001")
    assert (test["kind"], test["path"]) == ("test", "tests/TEST-00001.md")
    assert instance(model, "test_run_00001")["reference"] == "TEST-00001"
    assert model["problems"] == []


def test_paths_are_relative_to_the_project(hactors_root, populated):
    for item in build_model(hactors_root, populated.name)["artifacts"]:
        assert not item["path"].startswith(("/", "projects"))
        assert (populated / item["path"]).exists()


def test_an_unreadable_task_is_projected_with_empty_fields(hactors_root, populated):
    (populated / "tasks" / "TASK-00001.md").write_text("# Sin cabecera\n")
    model = build_model(hactors_root, populated.name)
    task = entry(model, "TASK-00001")
    assert (task["status"], task["actor"], task["title"]) == ("", "", "")
    assert any("tasks/TASK-00001.md" in problem for problem in model["problems"])


def test_an_rfc_without_identity_is_not_projected(hactors_root, populated):
    write_document(populated / "rfcs" / "sin-identidad.md", {"actions": ACTIONS})
    model = build_model(hactors_root, populated.name)
    assert "sin-identidad.md" not in [item["path"] for item in model["artifacts"]]
    assert model["problems"] == ["rfcs/sin-identidad.md: no declara 'rfc:'."]


def test_an_unreadable_record_is_projected_with_empty_fields(hactors_root, populated):
    (populated / "tasks" / "FND-00001.yaml").write_text("severity: [sin cerrar\n")
    model = build_model(hactors_root, populated.name)
    assert entry(model, "FND-00001")["status"] == ""
    assert any("tasks/FND-00001.yaml" in problem for problem in model["problems"])


# Instancias de ejecución.


def test_runs_project_their_hierarchy(hactors_root, populated):
    model = build_model(hactors_root, populated.name)
    assert [(item["id"], item["kind"], item["parent"]) for item in model["runs"]] == [
        ("workflow_run_00001", "workflow_run", ""),
        ("task_run_00001", "task_run", "workflow_run_00001"),
        ("rfc_run_00001", "rfc_run", "task_run_00001"),
        ("test_run_00001", "test_run", "rfc_run_00001"),
    ]
    assert instance(model, "task_run_00001")["path"] == "hactors/workflow_run_00001/task_run_00001"


def test_a_workflow_run_reads_its_state_from_global_state(hactors_root, populated, runs):
    set_state(runs["workflow_run"] / "manifest.yaml", "global_state",
              status="blocked", blocked_reason="Falta una evidencia")
    workflow = instance(build_model(hactors_root, populated.name), "workflow_run_00001")
    assert workflow["status"] == "blocked"
    assert workflow["blocked_reason"] == "Falta una evidencia"


def test_the_other_instances_read_their_state_from_state(hactors_root, populated, runs):
    set_state(runs["task_run"] / "manifest.yaml", "state", status="in-progress")
    model = build_model(hactors_root, populated.name)
    assert instance(model, "task_run_00001")["status"] == "in-progress"
    assert instance(model, "task_run_00001")["blocked_reason"] == ""


def test_a_pending_reference_is_projected_empty(hactors_root, populated):
    model = build_model(hactors_root, populated.name)
    assert instance(model, "workflow_run_00001")["reference"] == ""
    assert instance(model, "task_run_00001")["reference"] == ""


def test_a_declared_reference_is_projected_without_resolution(hactors_root, populated, runs):
    set_identity(runs["workflow_run"] / "manifest.yaml", task_ref="TASK-00001")
    set_identity(runs["rfc_run"] / "manifest.yaml", rfc_ref="RFC-A00001")
    model = build_model(hactors_root, populated.name)
    assert instance(model, "workflow_run_00001")["reference"] == "TASK-00001"
    assert instance(model, "rfc_run_00001")["reference"] == "RFC-A00001"
    assert model["problems"] == []


# export.


def test_export_writes_the_reading_model(hactors_root, populated):
    path = write_model(hactors_root, populated.name)
    assert path == populated / "views" / "project.json"
    written = json.loads(path.read_text())
    model = build_model(hactors_root, populated.name)
    written.pop("generated_at")
    model.pop("generated_at")
    assert written == model


def test_export_creates_views_without_touching_the_active_state(hactors_root, populated):
    state = hactors_root / "projects" / ".state.yaml"
    before = state.read_text()
    write_model(hactors_root, populated.name)
    assert state.read_text() == before


def test_export_command_reports_the_written_model(hactors_root, populated):
    result = invoke(hactors_root, "export")
    assert "Modelo de 'proj' exportado a:" in result.output
    assert json.loads((populated / "views" / "project.json").read_text())["project"] == "proj"


def test_export_requires_an_active_project(hactors_root):
    result = invoke(hactors_root, "export", expected=1)
    assert "No hay proyecto activo." in result.output


def test_export_reports_a_project_that_cannot_be_projected(hactors_root):
    (hactors_root / "projects" / "roto").mkdir()
    (hactors_root / "projects" / ".state.yaml").write_text(
        "active_project: roto\nactive_run_path: ''\n"
    )
    result = invoke(hactors_root, "export", expected=1)
    assert "Proyecto no encontrado o sin manifest: 'roto'." in result.output


# render.


def test_render_writes_the_viewer_and_every_board(hactors_root, populated):
    other = create_project("otro", hactors_root)
    written = render_views(hactors_root)
    assert set(written) == {
        populated / "views" / "index.html",
        other / "views" / "index.html",
        hactors_root / "projects" / "views" / "index.html",
    }
    assert written[-1] == hactors_root / "projects" / "views" / "index.html"
    assert all(path.is_file() for path in written)


def test_render_does_not_require_an_active_project(hactors_root, populated):
    (hactors_root / "projects" / ".state.yaml").unlink()
    render_views(hactors_root)
    assert "(proyecto activo)" not in viewer(hactors_root)
    assert ">proj</a>" in viewer(hactors_root)


def test_render_marks_the_active_project(hactors_root, populated):
    other = create_project("otro", hactors_root)
    render_views(hactors_root)
    assert viewer(hactors_root).count("(proyecto activo)") == 1
    assert "(proyecto activo)" in board(populated)
    assert "(proyecto activo)" not in board(other)


def test_render_lists_an_unprojectable_directory_with_its_reason(hactors_root, populated):
    (hactors_root / "projects" / "roto").mkdir()
    render_views(hactors_root)
    assert "no proyectable: Proyecto no encontrado o sin manifest: &#x27;roto&#x27;." in (
        viewer(hactors_root)
    )
    assert not (hactors_root / "projects" / "roto" / "views").exists()


def test_render_requires_a_projects_directory(hactors_root):
    with pytest.raises(ViewError) as excinfo:
        render_views(hactors_root / "specs")
    assert "No hay un directorio 'projects/'" in str(excinfo.value)


def test_render_command_reports_each_view(hactors_root, populated):
    result = invoke(hactors_root, "render")
    assert result.output.count("Vista escrita:") == 2
    assert "projects/views/index.html" in result.output


def test_render_does_not_write_the_reading_model(hactors_root, populated):
    render_views(hactors_root)
    assert not (populated / "views" / "project.json").exists()


def test_render_does_not_modify_any_artifact(hactors_root, populated):
    def artifacts() -> list:
        return sorted(
            (path.relative_to(populated).as_posix(), path.read_bytes())
            for path in populated.rglob("*")
            if path.is_file() and "views" not in path.relative_to(populated).parts
        )

    before = artifacts()
    render_views(hactors_root)
    assert artifacts() == before


def test_render_does_not_change_what_validate_reports(hactors_root, populated):
    before = invoke(hactors_root, "validate").output
    render_views(hactors_root)
    assert invoke(hactors_root, "validate").output == before
    assert build_model(hactors_root, populated.name)["problems"] == []


# El tablero.


def test_the_board_groups_artifacts_by_status(hactors_root, populated):
    render_views(hactors_root)
    text = board(populated)
    for status in ("draft", "accepted", "proposed", "approved", "open", "(sin declarar)"):
        assert f"<dt>{status}</dt>" in text


def test_the_board_groups_assignments_by_actor(hactors_root, populated):
    render_views(hactors_root)
    text = board(populated)
    for actor in ("human", "agent", "(sin actor declarado)"):
        assert f"<dt>{actor}</dt>" in text


def test_the_board_links_every_artifact_to_its_file(hactors_root, populated):
    render_views(hactors_root)
    text = board(populated)
    for item in build_model(hactors_root, populated.name)["artifacts"]:
        assert f"href='../{quote(item['path'])}'>{item['id']}</a>" in text


def test_the_board_shows_the_execution_branch(hactors_root, populated, runs):
    set_state(runs["rfc_run"] / "manifest.yaml", "state",
              status="blocked", blocked_reason="Falta una evidencia")
    render_views(hactors_root)
    text = board(populated)
    assert "<ul class='tree'>" in text
    assert "workflow_run_00001" in text
    assert "bloqueado: Falta una evidencia" in text


def test_the_board_shows_the_declared_edges(hactors_root, populated):
    write_relations(
        populated, [{"source": "TASK-00001", "target": "RFC-A00001", "relation": "derives"}]
    )
    render_views(hactors_root)
    text = board(populated)
    assert "<td><span class='kind'>derives</span></td>" in text
    assert "href='../tasks/TASK-00001.md'>TASK-00001</a>" in text


def test_the_board_reports_the_absence_of_edges(hactors_root, populated):
    render_views(hactors_root)
    assert "El manifest no registra ninguna arista." in board(populated)


def test_the_board_reproduces_the_counters(hactors_root, populated):
    render_views(hactors_root)
    text = board(populated)
    for name, value in manifest_data(populated)["counters"].items():
        assert f"<tr><td><code>{name}</code></td><td>{value}</td></tr>" in text


def test_the_board_reproduces_validate_problems_verbatim(hactors_root, populated, runs):
    set_identity(runs["workflow_run"] / "manifest.yaml", task_ref="TASK-00009")
    render_views(hactors_root)
    problems = validate_project(hactors_root, populated.name)
    assert problems
    section = board(populated).split("<h2>Inconsistencias</h2>")[1]
    listed = [unescape(item) for item in re.findall(r"<li>(.*?)</li>", section, re.DOTALL)]
    assert listed == problems


def test_the_board_reproduces_a_status_without_reinterpreting_it(hactors_root, project):
    task_id, path = create_task(hactors_root, project.name)
    path.write_text(path.read_text().replace("status: draft", "status: un-estado-inventado"))
    render_views(hactors_root)
    text = board(project)
    assert "un-estado-inventado" in text
    assert task_id in text


# El visor.


def test_the_viewer_lists_each_project_with_its_counts(hactors_root, populated):
    create_project("otro", hactors_root)
    render_views(hactors_root)
    text = viewer(hactors_root)
    assert (
        "<td>1 task · 1 rfc · 1 plan · 1 adr · 1 summary · 1 evidence · 1 finding · 1 harness</td>"
        in text
    )
    assert "<td>4</td>" in text
    assert ">otro</a>" in text


def test_the_viewer_links_every_board(hactors_root, populated):
    other = create_project("otro", hactors_root)
    render_views(hactors_root)
    text = viewer(hactors_root)
    for name in (populated.name, other.name):
        assert f"href='../{name}/views/index.html'>{name}</a>" in text


def test_the_viewer_reports_an_empty_root(hactors_root):
    render_views(hactors_root)
    assert "No hay ningún proyecto en la raíz." in viewer(hactors_root)


def test_a_views_directory_is_not_enumerated_as_a_project(hactors_root, populated):
    render_views(hactors_root)
    assert [item["name"] for item in root_models(hactors_root)] == ["proj"]
    rows = viewer(hactors_root).split("<tbody>")[1].split("</tbody>")[0]
    assert rows.count("<tr>") == 1


# Lo que una vista no hace.


def test_the_views_are_self_contained(hactors_root, populated):
    render_views(hactors_root)
    for text in (board(populated), viewer(hactors_root)):
        assert "<script" not in text
        assert "http://" not in text and "https://" not in text
        assert " src=" not in text
        assert "<link" not in text
        assert "<style>" in text


def test_interpolated_text_is_escaped(hactors_root, project):
    payload = "<script>alert('xss')</script>"
    create_task(hactors_root, project.name, task=payload)
    data = yaml.safe_load((project / "project.yaml").read_text())
    data["description"] = payload
    (project / "project.yaml").write_text(yaml.dump(data, sort_keys=False))
    render_views(hactors_root)
    for text in (board(project), viewer(hactors_root)):
        assert "<script>" not in text
        assert "&lt;script&gt;" in text


def test_the_links_stay_inside_the_project(hactors_root, populated):
    render_views(hactors_root)
    for href in re.findall(r"href='([^']*)'", board(populated)):
        assert href.startswith("../")
        assert "..%2F" not in href and "/../" not in href[3:]
