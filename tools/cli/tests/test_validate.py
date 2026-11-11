import shutil
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.harness_run import create_harness_run
from hactors_cli.core.plan_run import create_plan_run
from hactors_cli.core.project import create_project
from hactors_cli.core.rfc_run import create_rfc_run
from hactors_cli.core.task import create_task
from hactors_cli.core.task_run import create_task_run
from hactors_cli.core.test_run import create_test_run
from hactors_cli.core.validate import validate_project
from hactors_cli.core.workflow import create_workflow

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
# La RFC derivada declara su propia acción: repetir ACT-00001 rompería la igualdad del contador.
DERIVED_ACTIONS = [{**ACTIONS[0], "id": "ACT-00002"}]


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


def set_counter(project: Path, counter: str, value) -> None:
    path = project / "manifest.yaml"
    data = yaml.safe_load(path.read_text())
    data["counters"][counter] = value
    path.write_text(yaml.dump(data, sort_keys=False))


def active_run(hactors_root: Path) -> str:
    state = yaml.safe_load((hactors_root / "projects" / ".state.yaml").read_text())
    return state["active_run_path"]


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


def plan_document(project: Path, plan_id: str = "PLAN-00001", location: str = "plans") -> Path:
    path = write_document(project / location / f"{plan_id}.md", {"id": plan_id})
    bump_counter(project, "plan", plan_id)
    return path


def verification_document(project: Path, test_id: str = "TEST-00001", **extra) -> Path:
    path = write_document(project / "tests" / f"{test_id}.md", {"id": test_id, **extra})
    bump_counter(project, "test", test_id)
    return path


def task_document(project: Path, task_id: str = "TASK-00001", status: str = "draft") -> Path:
    path = project / "tasks" / f"{task_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ntask: \"\"\nexecution:\n  status: {status}\n---\n\n# {task_id}\n")
    bump_counter(project, "task", task_id)
    return path


def finding_document(
    project: Path,
    finding_id: str = "FND-00001",
    severity: str = "critical",
    state: str = "open",
    origin: str = "",
    field: str = "task",
) -> Path:
    path = project / "tasks" / f"{finding_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    source = {"execution": "", "artifact": "", "workflow": "", "task": "", "rfc": ""}
    source[field] = origin
    path.write_text(
        yaml.dump(
            {"id": finding_id, "severity": severity, "state": state, "source": source},
            sort_keys=False,
        )
    )
    bump_counter(project, "finding", finding_id)
    return path


def harness_package(project: Path, harness_id: str = "HRN-00001", version: str = "v001") -> Path:
    path = project / "harnesses" / harness_id / "versions" / version / "harness.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("id: HRN-00001\nversion: 1\n")
    return path


@pytest.fixture
def project(hactors_root):
    created = create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", created.name)
    return created


@pytest.fixture
def tree(hactors_root, project):
    """workflow_run → task_run → rfc_run → {plan_run, test_run → harness_run}."""
    workflow = create_workflow(hactors_root, project.name)
    task_run = create_task_run(hactors_root, project.name, _relative(project, workflow))
    rfc_run = create_rfc_run(hactors_root, project.name, _relative(project, task_run))
    plan_run = create_plan_run(hactors_root, project.name, _relative(project, rfc_run))
    test_run = create_test_run(hactors_root, project.name, _relative(project, rfc_run))
    harness_run = create_harness_run(hactors_root, project.name, _relative(project, test_run))
    return {
        "workflow_run": workflow,
        "task_run": task_run,
        "rfc_run": rfc_run,
        "plan_run": plan_run,
        "test_run": test_run,
        "harness_run": harness_run,
    }


def _relative(project: Path, path: Path) -> str:
    return path.relative_to(project).as_posix()


def set_identity(manifest: Path, **fields) -> None:
    data = yaml.safe_load(manifest.read_text())
    body = next(iter(data.values())) if "identity" not in data else data
    body["identity"].update(fields)
    manifest.write_text(yaml.dump(data, sort_keys=False))


def validate(hactors_root, project) -> list:
    return validate_project(hactors_root, project.name)


def test_project_without_documents_is_consistent(hactors_root, project, tree):
    assert validate(hactors_root, project) == []
    result = invoke(hactors_root, "validate")
    assert "Proyecto 'proj' sin inconsistencias." in result.output


def test_unresolved_task_ref_is_reported(hactors_root, project, tree):
    set_identity(tree["workflow_run"] / "manifest.yaml", task_ref="TASK-00001")
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "`task_ref` 'TASK-00001' no resuelve a tasks/TASK-00001.md." in problems[0]

    task_document(project)
    assert validate(hactors_root, project) == []


def test_unresolved_rfc_ref_is_reported(hactors_root, project, tree):
    set_identity(tree["rfc_run"] / "manifest.yaml", rfc_ref="RFC-A00001")
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "`rfc_ref` 'RFC-A00001' no resuelve a una RFC en rfcs/." in problems[0]

    rfc_document(project, actions=ACTIONS)
    assert validate(hactors_root, project) == []


@pytest.mark.parametrize("location", ["plans", "docs/plans"])
def test_unresolved_plan_ref_is_reported(hactors_root, project, tree, location):
    set_identity(tree["plan_run"] / "manifest.yaml", plan_ref="PLAN-00001")
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "`plan_ref` 'PLAN-00001' no resuelve a un PLAN en plans/ o docs/plans/." in problems[0]

    plan_document(project, location=location)
    assert validate(hactors_root, project) == []


def test_unresolved_harness_ref_is_reported(hactors_root, project, tree):
    set_identity(tree["harness_run"] / "manifest.yaml", harness_ref="HRN-00001@v001")
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "`harness_ref` 'HRN-00001@v001' no resuelve a " in problems[0]

    harness_package(project)
    assert validate(hactors_root, project) == []


@pytest.mark.parametrize("reference", ["HRN-00001", "HRN-1@v001", "HRN-00001@v1", "v001"])
def test_malformed_harness_ref_is_reported(hactors_root, project, tree, reference):
    set_identity(tree["harness_run"] / "manifest.yaml", harness_ref=reference)
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert f"Referencia de HARNESS inválida: '{reference}'" in problems[0]


def test_unresolved_test_ref_is_reported(hactors_root, project, tree):
    set_identity(tree["test_run"] / "manifest.yaml", test_ref="TEST-00001")
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "`test_ref` 'TEST-00001' no resuelve a un TEST en tests/." in problems[0]

    verification_document(project)
    assert validate(hactors_root, project) == []


def test_documents_without_identity_are_reported(hactors_root, project):
    write_document(project / "rfcs" / "sin-identidad.md", {"actions": ACTIONS})
    problems = validate(hactors_root, project)
    assert problems == ["rfcs/sin-identidad.md: no declara 'rfc:'."]


def test_test_without_identity_is_reported(hactors_root, project):
    write_document(project / "tests" / "sin-identidad.md", {"property": ""})
    assert validate(hactors_root, project) == ["tests/sin-identidad.md: no declara 'id:'."]


def test_repeated_test_identity_is_reported(hactors_root, project):
    verification_document(project)
    write_document(project / "tests" / "copia.md", {"id": "TEST-00001"})
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "identidad 'TEST-00001' repetida" in problems[0]
    assert "ya la declara tests/TEST-00001.md." in problems[0]


def test_repeated_identity_is_reported(hactors_root, project):
    rfc_document(project, actions=ACTIONS)
    write_document(project / "rfcs" / "copia.md", {"rfc": "RFC-A00001", "actions": ACTIONS})
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "identidad 'RFC-A00001' repetida" in problems[0]
    assert "ya la declara rfcs/RFC-A00001.md." in problems[0]


def test_summary_files_are_not_scanned_as_rfcs(hactors_root, project):
    write_document(project / "rfcs" / "RFC-A00001 - Summary.md", {"artifact": "RFC-A00001"})
    assert validate(hactors_root, project) == []


def test_actions_schema_is_checked_per_rfc(hactors_root, project):
    rfc_document(project, actions=[{**ACTIONS[0], "status": "cerrado"}])
    problems = validate(hactors_root, project)
    assert problems == [
        "rfcs/RFC-A00001.md: ACT-00001: `status` fuera de dominio: 'cerrado'."
    ]


def test_rfc_without_actions_field_is_reported(hactors_root, project):
    rfc_document(project, actions=None)
    problems = validate(hactors_root, project)
    assert problems == [
        "rfcs/RFC-A00001.md: Ningún bloque `yaml` del documento declara el campo `actions:`."
    ]


@pytest.mark.parametrize(
    "severity, state, status, expected",
    [
        ("critical", "open", "done", True),
        ("high", "open", "done", True),
        ("critical", "open", "draft", False),
        ("critical", "tracked", "done", False),
        ("medium", "open", "done", False),
    ],
)
def test_blocking_finding_against_closed_task(
    hactors_root, project, severity, state, status, expected
):
    task_document(project, status=status)
    finding_document(project, severity=severity, state=state, origin="TASK-00001")
    problems = validate(hactors_root, project)
    if not expected:
        assert problems == []
        return
    assert len(problems) == 1
    assert f"hallazgo `{severity}` en `open`" in problems[0]
    assert "con su TASK de origen TASK-00001 cerrada en `done`." in problems[0]


def test_origin_task_is_recovered_from_execution(hactors_root, project, tree):
    set_identity(tree["workflow_run"] / "manifest.yaml", task_ref="TASK-00001")
    task_document(project, status="done")
    finding_document(
        project, origin=_relative(project, tree["task_run"]), field="execution"
    )
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "TASK-00001 cerrada en `done`." in problems[0]


def test_origin_task_is_recovered_from_artifact(hactors_root, project):
    task_document(project, status="done")
    finding_document(project, origin="tasks/TASK-00001.md", field="artifact")
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert "TASK-00001 cerrada en `done`." in problems[0]


def test_undeterminable_origin_is_not_reported(hactors_root, project):
    task_document(project, status="done")
    finding_document(project, origin="rfcs/RFC-A00001.md", field="artifact")
    assert validate(hactors_root, project) == []


def test_illegible_document_is_reported(hactors_root, project):
    path = project / "rfcs" / "roto.md"
    path.write_text("# Roto\n\n```yaml\nrfc: [sin cerrar\n```\n")
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert problems[0].startswith("rfcs/roto.md: Bloque `yaml` ilegible:")


def test_illegible_manifest_is_reported(hactors_root, project, tree):
    (tree["rfc_run"] / "manifest.yaml").write_text("identity: [sin cerrar\n")
    problems = validate(hactors_root, project)
    assert len(problems) == 2
    assert problems[0].startswith(
        "YAML ilegible en 'hactors/workflow_run_00001/task_run_00001/rfc_run_00001/manifest.yaml':"
    )
    assert problems[1].startswith("projects/.state.yaml: la instancia activa")


def test_a_counter_below_an_observed_identity_is_reported(hactors_root, project):
    for number in range(1, 4):
        task_document(project, task_id=f"TASK-{number:05d}")
    task_document(project, task_id="TASK-00004")
    set_counter(project, "task", 2)
    assert validate(hactors_root, project) == [
        "manifest.yaml: el contador `task` vale 2 y existe la identidad 'TASK-00004'; "
        "debe ser mayor o igual que cualquier identidad de su tipo."
    ]

    bump_counter(project, "task", "TASK-00004")
    assert validate(hactors_root, project) == []


def test_a_counter_above_the_identities_present_is_reported(hactors_root, project):
    task_document(project)
    set_counter(project, "task", 3)
    assert validate(hactors_root, project) == [
        "manifest.yaml: el contador `task` vale 3 y hay 1 identidad(es) de su tipo presente(s); "
        "debe igualar exactamente esa cantidad."
    ]


def test_a_workflow_catalog_is_numbered_by_the_run_it_awaits(hactors_root, project):
    catalog = project / "workflows" / "WORKFLOW-00001" / "manifest.yaml"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(yaml.dump({"id": "WORKFLOW-00001", "versions": []}, sort_keys=False))
    assert validate(hactors_root, project) == [
        "manifest.yaml: el contador `workflow_run` vale 0 y existe la identidad 'WORKFLOW-00001'; "
        "debe ser mayor o igual que cualquier identidad de su tipo."
    ]

    # El catálogo no consume: hasta que su workflow_run exista, el número que anticipa sobra.
    set_counter(project, "workflow_run", 1)
    assert validate(hactors_root, project) == [
        "manifest.yaml: el contador `workflow_run` vale 1 y hay 0 identidad(es) de su tipo "
        "presente(s); debe igualar exactamente esa cantidad."
    ]

    paired_workflow_run(project, "WORKFLOW-00001")
    assert validate(hactors_root, project) == []


def test_a_run_counter_below_its_instances_is_reported(hactors_root, project, tree):
    set_counter(project, "test_run", 0)
    assert validate(hactors_root, project) == [
        "manifest.yaml: el contador `test_run` vale 0 y existe la identidad 'test_run_00001'; "
        "debe ser mayor o igual que cualquier identidad de su tipo."
    ]


def test_a_counter_that_is_not_an_integer_is_reported(hactors_root, project):
    task_document(project)
    set_counter(project, "task", "1")
    assert validate(hactors_root, project) == [
        "manifest.yaml: el contador `task` no es un entero no negativo."
    ]


def test_an_instance_outside_its_admitted_parent_is_reported(hactors_root, project, tree):
    misplaced = tree["workflow_run"] / "rfc_run_00001"
    misplaced.mkdir()
    (misplaced / "manifest.yaml").write_text("identity:\n  id: rfc_run_00001\n  rfc_ref: ''\n")
    set_counter(project, "rfc_run", 2)
    assert validate(hactors_root, project) == [
        "hactors/workflow_run_00001/rfc_run_00001: jerarquía inválida: "
        "rfc_run no puede vivir dentro de workflow_run."
    ]


def test_an_identity_that_does_not_match_its_directory_is_reported(hactors_root, project, tree):
    set_identity(tree["rfc_run"] / "manifest.yaml", id="rfc_run_00009")
    problems = validate(hactors_root, project)
    assert problems[0] == (
        "hactors/workflow_run_00001/task_run_00001/rfc_run_00001: "
        "`identity.id` no coincide con su componente de ruta 'rfc_run_00001'."
    )
    assert problems[1].startswith("projects/.state.yaml: la instancia activa")


def test_an_active_run_that_no_longer_exists_is_reported(hactors_root, project, tree):
    shutil.rmtree(tree["harness_run"])
    set_counter(project, "harness_run", 0)
    assert validate(hactors_root, project) == [
        f"projects/.state.yaml: la instancia activa '{active_run(hactors_root)}' no es válida: "
        "harness_run no encontrado o sin manifest: 'harness_run_00001'."
    ]


def test_a_project_without_active_run_reports_nothing_about_the_state(hactors_root, project):
    assert active_run(hactors_root) == ""
    assert validate(hactors_root, project) == []


def test_unknown_project_is_rejected(hactors_root):
    with pytest.raises(ValueError):
        validate_project(hactors_root, "inexistente")


def test_command_requires_active_project(hactors_root):
    create_project("proj", hactors_root)
    result = invoke(hactors_root, "validate", expected=1)
    assert "No hay proyecto activo" in result.output


def test_command_lists_every_problem_and_fails(hactors_root, project, tree):
    set_identity(tree["workflow_run"] / "manifest.yaml", task_ref="TASK-00009")
    set_identity(tree["rfc_run"] / "manifest.yaml", rfc_ref="RFC-A00002")
    rfc_document(project, actions=[{**ACTIONS[0], "id": "ACT-1"}])
    # 'ACT-1' no es una identidad ACT, así que ninguna acción consume el contador.
    set_counter(project, "action", 0)
    task_document(project, status="done")
    finding_document(project, origin="TASK-00001")
    result = invoke(hactors_root, "validate", expected=1)
    assert "`task_ref` 'TASK-00009' no resuelve" in result.output
    assert "`rfc_ref` 'RFC-A00002' no resuelve" in result.output
    assert "actions[1]: identificador inválido: 'ACT-1'." in result.output
    assert "hallazgo `critical` en `open`" in result.output
    assert "4 inconsistencia(s) en el proyecto 'proj'." in result.output


def test_created_task_is_consistent(hactors_root, project):
    create_task(hactors_root, project.name)
    assert validate(hactors_root, project) == []


def set_relations(project: Path, relations) -> None:
    manifest = project / "manifest.yaml"
    data = yaml.safe_load(manifest.read_text())
    data["relations"] = relations
    manifest.write_text(yaml.dump(data, sort_keys=False))


def edge(source: str, target: str, relation: str) -> dict:
    return {"source": source, "target": target, "relation": relation}


def record_document(project: Path, name: str, relations=None) -> Path:
    path = project / "tasks" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump({"id": name.split(".")[0], "relations": relations or []}, sort_keys=False)
    )
    counter = "evidence" if name.startswith("EVD-") else "finding"
    bump_counter(project, counter, name.split(".")[0])
    return path


def decision_document(project: Path, name: str = "ADR-00001 — decision.md") -> Path:
    path = project / "decisions" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Decisión\n")
    bump_counter(project, "adr", name.split(" ")[0])
    return path


def harness_catalog(project: Path, harness_id: str = "HRN-00001", **fields) -> Path:
    path = project / "harnesses" / harness_id / "manifest.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"id": harness_id, "relations": [], "versions": [], **fields}
    path.write_text(yaml.dump(data, sort_keys=False))
    bump_counter(project, "harness", harness_id)
    return path


def paired_workflow_run(project: Path, workflow_id: str) -> None:
    """El catálogo no consume contador: lo consume su ejecución, con el mismo número."""
    number = int(workflow_id.rsplit("-", 1)[-1])
    run = project / "hactors" / f"workflow_run_{number:05d}"
    run.mkdir(parents=True, exist_ok=True)
    (run / "manifest.yaml").write_text(
        yaml.dump(
            {
                run.name: {"identity": {"id": run.name, "task_ref": ""}},
                "global_state": {"status": "open"},
            },
            sort_keys=False,
        )
    )
    bump_counter(project, "workflow_run", run.name)


def workflow_catalog(project: Path, workflow_id: str = "WORKFLOW-00001") -> Path:
    path = project / "workflows" / workflow_id / "manifest.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump({"id": workflow_id, "versions": []}, sort_keys=False))
    paired_workflow_run(project, workflow_id)
    return path


def workflow_definition(
    project: Path, workflow_id: str = "WORKFLOW-00001", version: str = "v001"
) -> Path:
    path = project / "workflows" / workflow_id / "versions" / version / "workflow.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"id: {workflow_id}\nversion: 1\n")
    paired_workflow_run(project, workflow_id)
    return path


def test_relations_absent_or_empty_are_consistent(hactors_root, project):
    assert validate(hactors_root, project) == []
    set_relations(project, [])
    assert validate(hactors_root, project) == []


def test_relations_must_be_a_list(hactors_root, project):
    set_relations(project, "RFC-A00001")
    assert validate(hactors_root, project) == [
        "manifest.yaml: `relations` debe ser una lista, no str."
    ]


def test_relation_element_must_be_a_mapping(hactors_root, project):
    set_relations(project, ["RFC-A00001"])
    assert validate(hactors_root, project) == [
        "manifest.yaml: relations[1]: debe ser un mapeo, no str."
    ]


def test_relation_element_rejects_alien_fields(hactors_root, project):
    rfc_document(project, actions=ACTIONS)
    set_relations(project, [{**edge("RFC-A00001", "RFC-A00001", "derives"), "ruta": "rfcs/"}])
    assert validate(hactors_root, project) == [
        "manifest.yaml: relations[1]: campo ajeno al esquema: 'ruta'."
    ]


@pytest.mark.parametrize(
    "target, setup",
    [
        ("TASK-00001", lambda project: task_document(project)),
        ("PLAN-00001", lambda project: plan_document(project)),
        ("TEST-00001", lambda project: verification_document(project)),
        ("EVD-00001", lambda project: record_document(project, "EVD-00001.yaml")),
        ("FND-00001", lambda project: record_document(project, "FND-00001.yaml")),
        ("HRN-00001", lambda project: harness_catalog(project)),
        ("HRN-00001@v001", lambda project: harness_package(project)),
        ("WORKFLOW-00001", lambda project: workflow_catalog(project)),
        ("WORKFLOW-00001@v001", lambda project: workflow_definition(project)),
        ("ADR-00001", lambda project: decision_document(project)),
    ],
)
def test_target_resolves_against_its_artifact(hactors_root, project, target, setup):
    set_relations(project, [edge("RFC-A00001", target, "depends-on")])
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert f"`target` '{target}' no resuelve" in problems[0]

    setup(project)
    assert validate(hactors_root, project) == []


def test_rfc_target_resolves_against_its_document(hactors_root, project):
    rfc_document(project, actions=ACTIONS)
    set_relations(project, [edge("RFC-A00001", "RFC-F00001", "informs")])
    problems = validate(hactors_root, project)
    assert problems == [
        "manifest.yaml: relations[1]: `target` 'RFC-F00001' no resuelve a ningún artefacto del proyecto."
    ]

    rfc_document(project, name="RFC-F00001", actions=DERIVED_ACTIONS)
    assert validate(hactors_root, project) == []


def test_target_fragment_is_not_resolved(hactors_root, project):
    rfc_document(project, actions=ACTIONS)
    set_relations(project, [edge("EVD-00001", "RFC-A00001#C1", "verifies")])
    assert validate(hactors_root, project) == []


def test_local_identifier_without_its_artifact_is_reported(hactors_root, project):
    rfc_document(project, actions=ACTIONS)
    set_relations(project, [edge("EVD-00001", "ACT-00001", "verifies")])
    assert validate(hactors_root, project) == [
        "manifest.yaml: relations[1]: `target` 'ACT-00001' no resuelve a ningún artefacto del proyecto."
    ]


@pytest.mark.parametrize("target", ["mi_modulo/servicio", ""])
def test_targets_outside_the_defined_families_are_skipped(hactors_root, project, target):
    set_relations(project, [edge("RFC-A00001", target, "depends-on")])
    assert validate(hactors_root, project) == []


def test_harness_catalog_without_identity_is_reported(hactors_root, project):
    path = harness_catalog(project)
    data = yaml.safe_load(path.read_text())
    data.pop("id")
    path.write_text(yaml.dump(data, sort_keys=False))
    assert validate(hactors_root, project) == [
        "harnesses/HRN-00001/manifest.yaml: no declara 'id:'."
    ]


def test_rfc_origin_produces_an_inverted_derives_edge(hactors_root, project):
    rfc_document(project, actions=ACTIONS)
    rfc_document(project, name="RFC-F00001", actions=DERIVED_ACTIONS, origin="RFC-A00001")
    assert validate(hactors_root, project) == [
        "rfcs/RFC-F00001.md: el campo `origin` declara la arista "
        "{source: RFC-A00001, target: RFC-F00001, relation: derives}, "
        "que no consta en `relations` del manifest."
    ]

    set_relations(project, [edge("RFC-A00001", "RFC-F00001", "derives")])
    assert validate(hactors_root, project) == []


@pytest.mark.parametrize(
    "field, value, expected",
    [
        ("depends_on", ["RFC-A00001"], edge("RFC-F00001", "RFC-A00001", "depends-on")),
        ("supersedes", "RFC-A00001", edge("RFC-F00001", "RFC-A00001", "supersedes")),
        ("superseded_by", "RFC-A00001", edge("RFC-A00001", "RFC-F00001", "supersedes")),
    ],
)
def test_rfc_fields_produce_their_edge(hactors_root, project, field, value, expected):
    rfc_document(project, actions=ACTIONS)
    rfc_document(project, name="RFC-F00001", actions=DERIVED_ACTIONS, **{field: value})
    problems = validate(hactors_root, project)
    assert len(problems) == 1
    assert f"el campo `{field}` declara la arista" in problems[0]

    set_relations(project, [expected])
    assert validate(hactors_root, project) == []


def test_supersedes_declared_from_both_ends_is_one_edge(hactors_root, project):
    rfc_document(project, actions=ACTIONS, superseded_by="RFC-F00001")
    rfc_document(project, name="RFC-F00001", actions=DERIVED_ACTIONS, supersedes="RFC-A00001")
    problems = validate(hactors_root, project)
    assert problems == [
        "rfcs/RFC-A00001.md: el campo `superseded_by` declara la arista "
        "{source: RFC-F00001, target: RFC-A00001, relation: supersedes}, "
        "que no consta en `relations` del manifest."
    ]


def test_document_relation_list_is_represented_with_its_source(hactors_root, project):
    rfc_document(
        project,
        actions=ACTIONS,
        relations=[{"target": "RFC-F00001#C1", "relation": "informs"}],
    )
    assert validate(hactors_root, project) == [
        "rfcs/RFC-A00001.md: el campo `relations` declara la arista "
        "{source: RFC-A00001, target: RFC-F00001#C1, relation: informs}, "
        "que no consta en `relations` del manifest."
    ]


def test_test_relation_list_is_represented_with_its_source(hactors_root, project):
    verification_document(project)
    verification_document(
        project,
        test_id="TEST-00002",
        relations=[{"target": "TEST-00001", "relation": "derived_from"}],
    )
    assert validate(hactors_root, project) == [
        "tests/TEST-00002.md: el campo `relations` declara la arista "
        "{source: TEST-00002, target: TEST-00001, relation: derived_from}, "
        "que no consta en `relations` del manifest."
    ]

    set_relations(project, [edge("TEST-00002", "TEST-00001", "derived_from")])
    assert validate(hactors_root, project) == []


def test_record_relations_are_represented(hactors_root, project):
    record_document(
        project, "EVD-00001.yaml", relations=[{"target": "RFC-A00001#C1", "relation": "verifies"}]
    )
    record_document(
        project, "FND-00001.yaml", relations=[{"target": "HRN-00001", "relation": "affects"}]
    )
    assert validate(hactors_root, project) == [
        "tasks/EVD-00001.yaml: el campo `relations` declara la arista "
        "{source: EVD-00001, target: RFC-A00001#C1, relation: verifies}, "
        "que no consta en `relations` del manifest.",
        "tasks/FND-00001.yaml: el campo `relations` declara la arista "
        "{source: FND-00001, target: HRN-00001, relation: affects}, "
        "que no consta en `relations` del manifest.",
    ]


def test_harness_relations_use_the_identity_and_the_exact_version(hactors_root, project):
    harness_catalog(
        project,
        relations=[{"target": "HRN-00002@v001", "relation": "derived_from"}],
        versions=[
            {
                "version": 1,
                "relations": [{"target": "HRN-00002@v001", "relation": "compatible_with"}],
            }
        ],
    )
    assert validate(hactors_root, project) == [
        "harnesses/HRN-00001/manifest.yaml: el campo `relations` declara la arista "
        "{source: HRN-00001, target: HRN-00002@v001, relation: derived_from}, "
        "que no consta en `relations` del manifest.",
        "harnesses/HRN-00001/manifest.yaml: el campo `relations` declara la arista "
        "{source: HRN-00001@v001, target: HRN-00002@v001, relation: compatible_with}, "
        "que no consta en `relations` del manifest.",
    ]


def test_command_reports_graph_problems(hactors_root, project):
    rfc_document(project, actions=ACTIONS, origin="RFC-F00001")
    set_relations(project, [edge("RFC-A00001", "TASK-00009", "depends-on")])
    result = invoke(hactors_root, "validate", expected=1)
    assert "`target` 'TASK-00009' no resuelve" in result.output
    assert "el campo `origin` declara la arista" in result.output
    assert "2 inconsistencia(s) en el proyecto 'proj'." in result.output
