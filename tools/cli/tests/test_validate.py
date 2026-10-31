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


def write_document(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Documento\n\n```yaml\n{yaml.dump(data, sort_keys=False)}```\n")
    return path


def rfc_document(project: Path, name: str = "RFC-A00001", actions=None, **extra) -> Path:
    data = {"rfc": name, **extra}
    if actions is not None:
        data["actions"] = actions
    return write_document(project / "rfcs" / f"{name}.md", data)


def plan_document(project: Path, plan_id: str = "PLAN-00001", location: str = "plans") -> Path:
    return write_document(project / location / f"{plan_id}.md", {"id": plan_id})


def task_document(project: Path, task_id: str = "TASK-00001", status: str = "draft") -> Path:
    path = project / "tasks" / f"{task_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ntask: \"\"\nexecution:\n  status: {status}\n---\n\n# {task_id}\n")
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


def test_test_ref_is_not_resolved(hactors_root, project, tree):
    set_identity(tree["test_run"] / "manifest.yaml", test_ref="TEST-00001")
    assert validate(hactors_root, project) == []


def test_documents_without_identity_are_reported(hactors_root, project):
    write_document(project / "rfcs" / "sin-identidad.md", {"actions": ACTIONS})
    problems = validate(hactors_root, project)
    assert problems == ["rfcs/sin-identidad.md: no declara 'rfc:'."]


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
        "rfcs/RFC-A00001.md: AC-00001: `status` fuera de dominio: 'cerrado'."
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
    assert len(problems) == 1
    assert problems[0].startswith(
        "YAML ilegible en 'hactors/workflow_run_000001/task_run_000001/rfc_run_000001/manifest.yaml':"
    )


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
    rfc_document(project, actions=[{**ACTIONS[0], "id": "AC-1"}])
    task_document(project, status="done")
    finding_document(project, origin="TASK-00001")
    result = invoke(hactors_root, "validate", expected=1)
    assert "`task_ref` 'TASK-00009' no resuelve" in result.output
    assert "`rfc_ref` 'RFC-A00002' no resuelve" in result.output
    assert "actions[1]: identificador inválido: 'AC-1'." in result.output
    assert "hallazgo `critical` en `open`" in result.output
    assert "4 inconsistencia(s) en el proyecto 'proj'." in result.output


def test_created_task_is_consistent(hactors_root, project):
    create_task(hactors_root, project.name)
    assert validate(hactors_root, project) == []
