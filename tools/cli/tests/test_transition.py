import re
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.project import create_project
from hactors_cli.core.summary import SUMMARY_SUFFIX
from hactors_cli.core.transition import (
    ACTION_EDGES,
    ADR_EDGES,
    ADR_STATUSES,
    FAMILIES,
    FINDING_EDGES,
    FINDING_STATES,
    PLAN_EDGES,
    PLAN_STATUSES,
    RFC_EDGES,
    RFC_STATUSES,
    SUMMARY_EDGES,
    SUMMARY_STATUSES,
    TASK_EDGES,
    TASK_STATUSES,
    TRV_EDGES,
    TRV_STATUSES,
    WORKFLOW_EDGES,
    WORKFLOW_STATUSES,
    TransitionError,
    transition,
)

SPECS_TEMPLATES = Path(__file__).resolve().parents[3] / "specs" / "templates"
SPECS = SPECS_TEMPLATES.parent

TASK_PATH = "tasks/TASK-00001.md"
RFC_PATH = "rfcs/RFC-A00001.md"
SUCCESSOR_PATH = "rfcs/RFC-A00002.md"
SUMMARY_PATH = f"rfcs/RFC-A00001{SUMMARY_SUFFIX}"
RUN_SUMMARY_PATH = "hactors/workflow_run_000001/SUMMARY.md"
WORKFLOW_PATH = "workflows/WORKFLOW-00001/manifest.yaml"
PLAN_PATH = "plans/PLAN-00001.md"
ADR_PATH = "decisions/ADR-00001 — cierre-del-modo.md"
TRV_PATH = "trivial/TRV-00001 — errata.md"
FINDING_PATH = "rfcs/FND-00001.yaml"


def action(identity: str = "AC-00001", **extra) -> dict:
    element = {"id": identity, "type": "plan", "status": "pending", "actor": "human",
               "depends_on": [], "deliverable": "", "evidence": []}
    return {**element, **extra}


def write(project: Path, relpath: str, text: str) -> Path:
    path = project / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def template(name: str) -> dict:
    return yaml.safe_load((SPECS_TEMPLATES / name).read_text())


def frontmatter(data: dict) -> str:
    dumped = yaml.dump(data, sort_keys=False, allow_unicode=True)
    return f"---\n{dumped}---\n\nCuerpo.\n"


def block(data: dict, heading: str = "# Documento") -> str:
    dumped = yaml.dump(data, sort_keys=False, allow_unicode=True)
    return f"{heading}\n\n```yaml\n{dumped}```\n"


def task(project: Path, status: str = "draft", rfcs=()) -> Path:
    data = template("task_template.yaml")
    data["rfcs"] = list(rfcs)
    data["execution"]["status"] = status
    return write(project, TASK_PATH, frontmatter(data))


def rfc(project: Path, status: str = "draft", actions=(), relpath: str = RFC_PATH,
        identity: str = "RFC-A00001", **extra) -> Path:
    head = {"rfc": identity, "title": "", "status": status, **extra}
    body = {"context": "", "actions": list(actions)}
    dumped = yaml.dump(head, sort_keys=False, allow_unicode=True)
    inner = yaml.dump(body, sort_keys=False, allow_unicode=True)
    return write(project, relpath, f"# RFC\n\n```yaml\n{dumped}```\n\n```yaml\n{inner}```\n")


def summary(project: Path, artifact: str, status: str = "in-progress",
            relpath: str = SUMMARY_PATH) -> Path:
    data = template("summary_template.yaml")
    data["artifact"] = artifact
    data["status"] = status
    return write(project, relpath, frontmatter(data))


def workflow(project: Path, status: str = "proposed", identity: str = "WORKFLOW-00001") -> Path:
    data = {"id": identity, "title": "", "status": status, "current_version": None, "versions": []}
    path = f"workflows/{identity}/manifest.yaml"
    return write(project, path, yaml.dump(data, sort_keys=False, allow_unicode=True))


def plan(project: Path, status: str = "draft", relpath: str = PLAN_PATH) -> Path:
    return write(project, relpath, block({"id": "PLAN-00001", "title": "", "status": status}, "# Plan"))


def adr(project: Path, status: str = "proposed", cabecera: bool = False) -> Path:
    data = template("adr_template.yaml")
    data["adr"] = "ADR-00001"
    data["status"] = status
    text = block(data, "# Decisión\n\n## Cabecera") if cabecera else frontmatter(data)
    return write(project, ADR_PATH, text)


def trivial(base: Path, status: str = "proposed") -> Path:
    data = {"id": "TRV-00001", "title": "", "date": "", "proposed_by": "human",
            "status": status, "batch": False}
    return write(base, TRV_PATH, block(data, "# Cambio trivial\n\n## Metadatos"))


def finding(project: Path, state: str = "open", severity: str = "low",
            relpath: str = FINDING_PATH, **source) -> Path:
    data = template("finding_template.yaml")
    data["id"] = Path(relpath).stem
    data["state"] = state
    data["severity"] = severity
    data["source"] = source
    return write(project, relpath, yaml.dump(data, sort_keys=False, allow_unicode=True))


def invoke(root, *args, expected=0):
    result = CliRunner().invoke(cli, [*args, "--root", str(root)])
    assert result.exit_code == expected, result.output
    assert "Traceback" not in result.output
    return result


@pytest.fixture
def project(hactors_root):
    created = create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", created.name)
    return created


def changed_line(before: str, after: str) -> tuple[str, str]:
    previous, updated = before.splitlines(), after.splitlines()
    assert len(previous) == len(updated)
    differences = [(a, b) for a, b in zip(previous, updated) if a != b]
    assert len(differences) == 1
    return differences[0]


def go(root, project, relpath, to, identity=None):
    return transition(root, project.name, relpath, to, identity)


# Las nueve familias de la tabla de la sección 17.


@pytest.mark.parametrize(
    "prepare, relpath, to, expected",
    [
        (lambda p: task(p), TASK_PATH, "approved", "  status: approved"),
        (lambda p: rfc(p), RFC_PATH, "approved", "status: approved"),
        (lambda p: summary(p, RFC_PATH), SUMMARY_PATH, "consolidated", "status: consolidated"),
        (lambda p: workflow(p), WORKFLOW_PATH, "active", "status: active"),
        (lambda p: plan(p), PLAN_PATH, "proposed", "status: proposed"),
        (lambda p: adr(p), ADR_PATH, "accepted", "status: accepted"),
        (lambda p: adr(p, cabecera=True), ADR_PATH, "accepted", "status: accepted"),
        (lambda p: trivial(p), TRV_PATH, "approved", "status: approved"),
        (lambda p: finding(p), FINDING_PATH, "tracked", "state: tracked"),
    ],
)
def test_each_family_rewrites_its_own_field(hactors_root, project, prepare, relpath, to, expected):
    path = prepare(project)
    before = path.read_text()
    subject, where, previous = go(hactors_root, project, relpath, to)
    assert where == relpath
    assert subject
    assert previous != to
    assert changed_line(before, path.read_text())[1] == expected


def test_the_task_identity_is_its_filename(hactors_root, project):
    task(project)
    assert go(hactors_root, project, TASK_PATH, "approved")[0] == "TASK-00001"


def test_the_rfc_identity_is_its_declared_field(hactors_root, project):
    rfc(project, identity="RFC-D00007")
    assert go(hactors_root, project, RFC_PATH, "approved")[0] == "RFC-D00007"


def test_the_summary_identity_is_the_artifact_it_summarises(hactors_root, project):
    summary(project, RFC_PATH)
    assert go(hactors_root, project, SUMMARY_PATH, "consolidated")[0] == RFC_PATH


def test_the_workflow_run_summary_is_also_a_summary(hactors_root, project):
    summary(project, "hactors/workflow_run_000001", relpath=RUN_SUMMARY_PATH)
    assert go(hactors_root, project, RUN_SUMMARY_PATH, "consolidated")[0] == "hactors/workflow_run_000001"


def test_a_plan_also_lives_under_docs(hactors_root, project):
    plan(project, relpath="docs/plans/PLAN-00001.md")
    assert go(hactors_root, project, "docs/plans/PLAN-00001.md", "proposed")[0] == "PLAN-00001"


def test_a_finding_is_recognised_wherever_it_lives(hactors_root, project):
    finding(project, relpath="hactors/workflow_run_000001/FND-00002.yaml")
    subject, _, _ = go(hactors_root, project, "hactors/workflow_run_000001/FND-00002.yaml", "tracked")
    assert subject == "FND-00002"


# Escritura puntual.


def test_the_rest_of_the_file_is_preserved_byte_for_byte(hactors_root, project):
    path = task(project)
    before = path.read_text()
    go(hactors_root, project, TASK_PATH, "approved")
    after = path.read_text()
    assert before.replace("status: draft", "status: approved") == after


def test_a_quoted_value_keeps_its_quotes(hactors_root, project):
    path = summary(project, RFC_PATH)
    path.write_text(path.read_text().replace("status: in-progress", 'status: "in-progress"'))
    go(hactors_root, project, SUMMARY_PATH, "consolidated")
    assert 'status: "consolidated"' in path.read_text()


def test_a_single_quoted_value_keeps_its_quotes(hactors_root, project):
    path = rfc(project)
    path.write_text(path.read_text().replace("status: draft", "status: 'draft'"))
    go(hactors_root, project, RFC_PATH, "approved")
    assert "status: 'approved'" in path.read_text()


def test_a_trailing_comment_survives(hactors_root, project):
    path = finding(project)
    path.write_text(path.read_text().replace("state: open", "state: open  # sin acción"))
    go(hactors_root, project, FINDING_PATH, "tracked")
    assert "state: tracked  # sin acción" in path.read_text()


def test_the_separator_is_preserved(hactors_root, project):
    path = plan(project)
    path.write_text(path.read_text().replace("status: draft", "status:    draft"))
    go(hactors_root, project, PLAN_PATH, "proposed")
    assert "status:    proposed" in path.read_text()


def test_an_action_is_rewritten_inside_the_actions_interval(hactors_root, project):
    path = rfc(project, actions=[action(), action("AC-00002")])
    before = path.read_text()
    subject, _, previous = go(hactors_root, project, RFC_PATH, "in-progress", "AC-00002")
    assert (subject, previous) == ("AC-00002", "pending")
    assert changed_line(before, path.read_text()) == ("  status: pending", "  status: in-progress")
    assert before.count("status: pending") == 2
    assert path.read_text().count("status: pending") == 1


@pytest.mark.parametrize("indent", ["", "  "])
def test_either_list_indentation_of_the_actions_field_is_readable(hactors_root, project, indent):
    text = (
        "# RFC\n\n```yaml\nrfc: RFC-A00001\nstatus: draft\n```\n\n"
        f"```yaml\nactions:\n{indent}- id: AC-00001\n{indent}  status: pending\n```\n"
    )
    path = write(project, RFC_PATH, text)
    assert go(hactors_root, project, RFC_PATH, "in-progress", "AC-00001")[2] == "pending"
    assert changed_line(text, path.read_text()) == (
        f"{indent}  status: pending", f"{indent}  status: in-progress"
    )


def test_no_counter_is_consumed(hactors_root, project):
    manifest = project / "manifest.yaml"
    before = manifest.read_text()
    task(project)
    go(hactors_root, project, TASK_PATH, "approved")
    assert manifest.read_text() == before


def test_the_active_state_is_untouched(hactors_root, project):
    state = hactors_root / "projects" / ".state.yaml"
    before = state.read_text()
    task(project)
    go(hactors_root, project, TASK_PATH, "approved")
    assert state.read_text() == before


# Comprobación 1: el objetivo.


@pytest.mark.parametrize(
    "relpath",
    ["rfcs", "/etc/passwd", "rfcs/../manifest.yaml", "rfcs\\RFC-A00001.md", "rfcs//x.md",
     "rfcs/ausente.md", "./rfcs/RFC-A00001.md"],
)
def test_a_target_that_is_not_a_project_file_is_rejected(hactors_root, project, relpath):
    rfc(project)
    with pytest.raises(TransitionError):
        go(hactors_root, project, relpath, "approved")


def test_a_symlink_is_rejected(hactors_root, project):
    path = rfc(project)
    link = project / "rfcs" / "RFC-A00002.md"
    link.symlink_to(path)
    with pytest.raises(TransitionError, match="enlaces simbólicos"):
        go(hactors_root, project, "rfcs/RFC-A00002.md", "approved")


# El TRV de la raíz de la copia, la segunda ubicación que prescribe TRIVIAL.md.


def test_the_trivial_of_the_copy_root_is_reachable(hactors_root, project):
    path = trivial(hactors_root)
    before = path.read_text()
    assert go(hactors_root, project, TRV_PATH, "approved") == ("TRV-00001", TRV_PATH, "proposed")
    assert changed_line(before, path.read_text())[1] == "status: approved"


def test_the_command_rewrites_the_trivial_of_the_copy_root(hactors_root, project):
    trivial(hactors_root)
    result = invoke(hactors_root, "transition", "--artifact", TRV_PATH, "--to", "approved")
    assert f"TRV-00001 en '{TRV_PATH}': proposed → approved" in result.output
    assert "status: approved" in (hactors_root / TRV_PATH).read_text()


def test_a_trivial_of_the_project_takes_precedence_over_the_root_one(hactors_root, project):
    at_root = trivial(hactors_root)
    own = trivial(project)
    go(hactors_root, project, TRV_PATH, "approved")
    assert "status: proposed" in at_root.read_text()
    assert "status: approved" in own.read_text()


def test_a_trivial_absent_from_both_locations_is_not_found(hactors_root, project):
    with pytest.raises(TransitionError, match="no encontrado"):
        go(hactors_root, project, TRV_PATH, "approved")


@pytest.mark.parametrize(
    "prepare, relpath",
    [
        (lambda base: write(base, TASK_PATH, frontmatter({"execution": {"status": "draft"}})),
         TASK_PATH),
        (lambda base: write(base, "trivial/notas.md", block({"id": "TRV-00001", "status": "proposed"})),
         "trivial/notas.md"),
        (lambda base: write(base, "trivial/sub/TRV-00002 — otra.md",
                            block({"id": "TRV-00002", "status": "proposed"})),
         "trivial/sub/TRV-00002 — otra.md"),
    ],
)
def test_no_other_target_resolves_outside_the_project(hactors_root, project, prepare, relpath):
    prepare(hactors_root)
    with pytest.raises(TransitionError, match="no encontrado"):
        go(hactors_root, project, relpath, "approved")


@pytest.mark.parametrize(
    "prepare, relpath",
    [
        (lambda p: write(p, "hactors/workflow_run_000001/manifest.yaml", "identity:\n  id: x\n"),
         "hactors/workflow_run_000001/manifest.yaml"),
        (lambda p: write(p, "harnesses/HRN-00001/manifest.yaml", "id: HRN-00001\nstatus: active\n"),
         "harnesses/HRN-00001/manifest.yaml"),
        (lambda p: write(p, "harnesses/HRN-00001/versions/v001/harness.yaml", "status: draft\n"),
         "harnesses/HRN-00001/versions/v001/harness.yaml"),
        (lambda p: write(p, "tests/TEST-00001.md", block({"id": "TEST-00001", "status": "draft"})),
         "tests/TEST-00001.md"),
        (lambda p: write(p, "standards/LANGUAGE.md", "# Perfil\n"), "standards/LANGUAGE.md"),
        (lambda p: write(p, "workflows/WORKFLOW-00001/versions/v001/workflow.yaml", "status: draft\n"),
         "workflows/WORKFLOW-00001/versions/v001/workflow.yaml"),
    ],
)
def test_a_target_outside_the_table_is_rejected(hactors_root, project, prepare, relpath):
    prepare(project)
    with pytest.raises(TransitionError, match="ninguna familia"):
        go(hactors_root, project, relpath, "approved")


@pytest.mark.parametrize("relpath", ["rfcs/EVD-00001.yaml", "rfcs/notas.md"])
def test_a_file_in_rfcs_that_declares_no_identity_is_rejected(hactors_root, project, relpath):
    write(project, relpath, "# Sin identidad\n")
    with pytest.raises(TransitionError, match="no declara 'rfc:'"):
        go(hactors_root, project, relpath, "approved")


def test_the_manifest_of_a_run_instance_is_rejected(hactors_root, project):
    invoke(hactors_root, "create-workflow")
    with pytest.raises(TransitionError, match="ninguna familia"):
        go(hactors_root, project, "hactors/workflow_run_000001/manifest.yaml", "active")


@pytest.mark.parametrize(
    "prepare, relpath",
    [
        (lambda p: task(p), TASK_PATH),
        (lambda p: summary(p, RFC_PATH), SUMMARY_PATH),
        (lambda p: workflow(p), WORKFLOW_PATH),
        (lambda p: plan(p), PLAN_PATH),
        (lambda p: adr(p), ADR_PATH),
        (lambda p: trivial(p), TRV_PATH),
        (lambda p: finding(p), FINDING_PATH),
    ],
)
def test_an_element_identifier_is_rejected_by_a_family_without_elements(
    hactors_root, project, prepare, relpath
):
    prepare(project)
    with pytest.raises(TransitionError, match="no tiene elementos"):
        go(hactors_root, project, relpath, "done", "AC-00001")


def test_an_unknown_action_is_rejected(hactors_root, project):
    path = rfc(project, actions=[action()])
    before = path.read_text()
    with pytest.raises(TransitionError, match="no declara la acción 'AC-00009'"):
        go(hactors_root, project, RFC_PATH, "in-progress", "AC-00009")
    assert path.read_text() == before


def test_an_rfc_without_an_actions_field_rejects_an_identifier(hactors_root, project):
    write(project, RFC_PATH, "# RFC\n\n```yaml\nrfc: RFC-A00001\nstatus: draft\n```\n")
    with pytest.raises(TransitionError, match="Ningún bloque"):
        go(hactors_root, project, RFC_PATH, "approved", "AC-00001")


# Comprobación 2: el campo de estado.


@pytest.mark.parametrize(
    "text",
    [
        "---\ntask: x\n---\n\nCuerpo.\n",
        "---\ntask: x\nexecution:\n  target_status: done\n---\n\nCuerpo.\n",
        "---\ntask: x\nexecution:\n  status: finished\n---\n\nCuerpo.\n",
        "---\ntask: x\nexecution:\n  status: ''\n---\n\nCuerpo.\n",
    ],
)
def test_a_task_without_a_readable_state_is_rejected(hactors_root, project, text):
    write(project, TASK_PATH, text)
    with pytest.raises(TransitionError):
        go(hactors_root, project, TASK_PATH, "approved")


def test_a_state_outside_the_vocabulary_is_a_defective_document(hactors_root, project):
    path = finding(project, state="cerrado")
    with pytest.raises(TransitionError, match="fuera de los estados de Hallazgo"):
        go(hactors_root, project, FINDING_PATH, "tracked")
    assert "state: cerrado" in path.read_text()


def test_a_document_without_frontmatter_is_rejected(hactors_root, project):
    write(project, TASK_PATH, "# TASK-00001\n\nSin cabecera.\n")
    with pytest.raises(TransitionError, match="frontmatter"):
        go(hactors_root, project, TASK_PATH, "approved")


def test_a_workflow_catalogue_without_identity_is_rejected(hactors_root, project):
    write(project, WORKFLOW_PATH, "title: x\nstatus: proposed\n")
    with pytest.raises(TransitionError, match="no declara 'id:'"):
        go(hactors_root, project, WORKFLOW_PATH, "active")


# Comprobación 3: el destino.


def test_a_destination_outside_the_vocabulary_is_rejected(hactors_root, project):
    task(project)
    with pytest.raises(TransitionError, match="'merged' no es un estado de TASK"):
        go(hactors_root, project, TASK_PATH, "merged")


def test_repeating_the_current_state_is_not_a_transition(hactors_root, project):
    path = task(project, status="draft")
    before = path.read_text()
    with pytest.raises(TransitionError, match="ya está en 'draft'"):
        go(hactors_root, project, TASK_PATH, "draft")
    assert path.read_text() == before


# Comprobación 4: la arista.


@pytest.mark.parametrize(
    "prepare, relpath, status, to",
    [
        (lambda p: task(p, "draft"), TASK_PATH, "draft", "done"),
        (lambda p: task(p, "implemented"), TASK_PATH, "implemented", "in-progress"),
        (lambda p: task(p, "done"), TASK_PATH, "done", "cancelled"),
        (lambda p: rfc(p, "proposed"), RFC_PATH, "proposed", "done"),
        (lambda p: rfc(p, "validated"), RFC_PATH, "validated", "in-progress"),
        (lambda p: workflow(p, "proposed"), WORKFLOW_PATH, "proposed", "closed"),
        (lambda p: workflow(p, "closed"), WORKFLOW_PATH, "closed", "active"),
        (lambda p: plan(p, "draft"), PLAN_PATH, "draft", "completed"),
        (lambda p: adr(p, "accepted"), ADR_PATH, "accepted", "rejected"),
        (lambda p: trivial(p, "approved"), TRV_PATH, "approved", "rejected"),
        (lambda p: finding(p, "resolved"), FINDING_PATH, "resolved", "open"),
    ],
)
def test_an_edge_the_norm_does_not_admit_is_rejected(hactors_root, project, prepare, relpath, status, to):
    path = prepare(project)
    before = path.read_text()
    with pytest.raises(TransitionError, match="no admite la transición"):
        go(hactors_root, project, relpath, to)
    assert path.read_text() == before


@pytest.mark.parametrize(
    "family_edges, prepare, relpath, chain",
    [
        (TASK_EDGES, lambda p: task(p, "proposed"), TASK_PATH,
         ["draft", "approved", "in-progress", "implemented", "tested", "done"]),
        (RFC_EDGES, lambda p: rfc(p, "proposed"), RFC_PATH,
         ["draft", "approved", "in-progress", "implemented", "tested", "under_review",
          "validated", "merged", "done"]),
        (WORKFLOW_EDGES, lambda p: workflow(p), WORKFLOW_PATH, ["active", "closing", "closed"]),
        (PLAN_EDGES, lambda p: plan(p), PLAN_PATH, ["proposed", "approved", "completed"]),
        (ADR_EDGES, lambda p: adr(p), ADR_PATH, ["accepted", "superseded"]),
        (TRV_EDGES, lambda p: trivial(p), TRV_PATH, ["approved", "done"]),
        (FINDING_EDGES, lambda p: finding(p), FINDING_PATH, ["tracked", "resolved"]),
    ],
)
def test_the_whole_chain_is_walkable(hactors_root, project, family_edges, prepare, relpath, chain):
    prepare(project)
    for to in chain:
        assert go(hactors_root, project, relpath, to)[2] != to
    assert all((left, right) in family_edges for left, right in zip(chain, chain[1:]))


def test_an_rfc_returns_to_in_progress(hactors_root, project):
    for status in ("implemented", "tested", "under_review"):
        rfc(project, status)
        assert go(hactors_root, project, RFC_PATH, "in-progress")[2] == status


def test_a_task_has_no_return_edge(hactors_root, project):
    task(project, "implemented")
    with pytest.raises(TransitionError, match="no admite la transición"):
        go(hactors_root, project, TASK_PATH, "in-progress")


def test_a_summary_reopens(hactors_root, project):
    summary(project, RFC_PATH, "consolidated")
    assert go(hactors_root, project, SUMMARY_PATH, "in-progress")[2] == "consolidated"


def test_an_action_blocks_and_unblocks(hactors_root, project):
    rfc(project, actions=[action()])
    assert go(hactors_root, project, RFC_PATH, "blocked", "AC-00001")[2] == "pending"
    assert go(hactors_root, project, RFC_PATH, "pending", "AC-00001")[2] == "blocked"


# Comprobación 5: TASK en done.


def test_a_task_closes_with_its_scope_done(hactors_root, project):
    rfc(project, "done")
    task(project, "tested", rfcs=["RFC-A00001"])
    assert go(hactors_root, project, TASK_PATH, "done")[2] == "tested"


def test_a_task_closes_without_declaring_any_rfc(hactors_root, project):
    task(project, "tested")
    assert go(hactors_root, project, TASK_PATH, "done")[2] == "tested"


def test_a_task_does_not_close_with_its_scope_open(hactors_root, project):
    rfc(project, "under_review")
    path = task(project, "tested", rfcs=["RFC-A00001"])
    with pytest.raises(TransitionError, match="está en 'under_review', no en `done`"):
        go(hactors_root, project, TASK_PATH, "done")
    assert "status: tested" in path.read_text()


def test_a_task_does_not_close_with_an_unregistered_rfc(hactors_root, project):
    task(project, "tested", rfcs=["RFC-A00009"])
    with pytest.raises(TransitionError, match="no existe en rfcs/"):
        go(hactors_root, project, TASK_PATH, "done")


def test_a_superseded_rfc_needs_its_successor_in_scope(hactors_root, project):
    rfc(project, "superseded", relpath=RFC_PATH, identity="RFC-A00001", superseded_by="RFC-A00002")
    rfc(project, "done", relpath=SUCCESSOR_PATH, identity="RFC-A00002")
    task(project, "tested", rfcs=["RFC-A00001"])
    with pytest.raises(TransitionError, match="no consta en `rfcs:`"):
        go(hactors_root, project, TASK_PATH, "done")


def test_a_superseded_rfc_needs_its_successor_done(hactors_root, project):
    rfc(project, "superseded", relpath=RFC_PATH, identity="RFC-A00001", superseded_by="RFC-A00002")
    rfc(project, "validated", relpath=SUCCESSOR_PATH, identity="RFC-A00002")
    task(project, "tested", rfcs=["RFC-A00001", "RFC-A00002"])
    with pytest.raises(TransitionError, match="no está en `done`"):
        go(hactors_root, project, TASK_PATH, "done")


def test_an_incorporated_successor_closes_the_task(hactors_root, project):
    rfc(project, "superseded", relpath=RFC_PATH, identity="RFC-A00001", superseded_by="RFC-A00002")
    rfc(project, "done", relpath=SUCCESSOR_PATH, identity="RFC-A00002")
    task(project, "tested", rfcs=["RFC-A00001", "RFC-A00002"])
    assert go(hactors_root, project, TASK_PATH, "done")[2] == "tested"


def test_a_superseded_rfc_without_successor_is_reported(hactors_root, project):
    rfc(project, "superseded", relpath=RFC_PATH, identity="RFC-A00001", superseded_by=None)
    task(project, "tested", rfcs=["RFC-A00001"])
    with pytest.raises(TransitionError, match="sin `superseded_by`"):
        go(hactors_root, project, TASK_PATH, "done")


@pytest.mark.parametrize("severity", ["critical", "high"])
def test_a_blocking_finding_keeps_its_task_open(hactors_root, project, severity):
    task(project, "tested")
    finding(project, severity=severity, state="open", task="TASK-00001")
    with pytest.raises(TransitionError, match="bloquea TASK 'TASK-00001'"):
        go(hactors_root, project, TASK_PATH, "done")


def test_a_blocking_finding_reached_through_its_execution_keeps_the_task_open(hactors_root, project):
    invoke(hactors_root, "create-workflow", "--task-ref", "TASK-00001")
    task(project, "tested")
    finding(project, severity="critical", execution="hactors/workflow_run_000001")
    with pytest.raises(TransitionError, match="bloquea TASK 'TASK-00001'"):
        go(hactors_root, project, TASK_PATH, "done")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"severity": "medium", "task": "TASK-00001"},
        {"severity": "critical", "state": "tracked", "task": "TASK-00001"},
        {"severity": "critical", "task": "TASK-00002"},
        {"severity": "critical", "artifact": RFC_PATH},
    ],
)
def test_a_finding_that_does_not_block_lets_the_task_close(hactors_root, project, kwargs):
    task(project, "tested")
    finding(project, **kwargs)
    assert go(hactors_root, project, TASK_PATH, "done")[2] == "tested"


def test_an_unreadable_finding_is_reported(hactors_root, project):
    task(project, "tested")
    write(project, FINDING_PATH, "state: [\n")
    with pytest.raises(TransitionError, match="ilegible"):
        go(hactors_root, project, TASK_PATH, "done")


# Comprobación 5: RFC en done y acción en completed.


def test_an_rfc_closes_with_every_action_completed(hactors_root, project):
    rfc(project, "merged", actions=[action(status="completed", evidence=["EVD-00001"])])
    assert go(hactors_root, project, RFC_PATH, "done")[2] == "merged"


def test_an_rfc_closes_without_actions(hactors_root, project):
    rfc(project, "merged")
    assert go(hactors_root, project, RFC_PATH, "done")[2] == "merged"


def test_an_rfc_does_not_close_with_a_pending_action(hactors_root, project):
    path = rfc(project, "merged", actions=[action()])
    with pytest.raises(TransitionError, match="la acción 'AC-00001' no está en `completed`"):
        go(hactors_root, project, RFC_PATH, "done")
    assert "status: merged" in path.read_text()


@pytest.mark.parametrize("status", ["cancelled", "superseded"])
def test_a_disposed_action_also_blocks_the_rfc(hactors_root, project, status):
    rfc(project, "merged", actions=[action(status=status)])
    with pytest.raises(TransitionError, match="no está en `completed`"):
        go(hactors_root, project, RFC_PATH, "done")


def test_an_action_completes_with_evidence(hactors_root, project):
    rfc(project, actions=[action(status="in-progress", evidence=["EVD-00001"])])
    assert go(hactors_root, project, RFC_PATH, "completed", "AC-00001")[2] == "in-progress"


def test_an_action_does_not_complete_without_evidence(hactors_root, project):
    path = rfc(project, actions=[action(status="in-progress")])
    with pytest.raises(TransitionError, match="no declara evidencia"):
        go(hactors_root, project, RFC_PATH, "completed", "AC-00001")
    assert "status: in-progress" in path.read_text()


# Comprobación 5: resumen en consolidated y WORKFLOW en closed.


def test_a_summary_consolidates_without_blocking_findings(hactors_root, project):
    rfc(project, "done")
    summary(project, RFC_PATH)
    assert go(hactors_root, project, SUMMARY_PATH, "consolidated")[2] == "in-progress"


def test_a_blocking_finding_on_the_summarised_rfc_blocks_the_summary(hactors_root, project):
    summary(project, RFC_PATH)
    finding(project, severity="high", artifact=RFC_PATH)
    with pytest.raises(TransitionError, match="bloquea Resumen"):
        go(hactors_root, project, SUMMARY_PATH, "consolidated")


def test_a_blocking_finding_on_another_artifact_does_not_block_the_summary(hactors_root, project):
    summary(project, RFC_PATH)
    finding(project, severity="high", artifact=SUCCESSOR_PATH)
    assert go(hactors_root, project, SUMMARY_PATH, "consolidated")[2] == "in-progress"


@pytest.mark.parametrize(
    "execution", ["hactors/workflow_run_000001", "hactors/workflow_run_000001/task_run_000002"]
)
def test_a_blocking_finding_inside_the_run_subtree_blocks_its_summary(hactors_root, project, execution):
    summary(project, "hactors/workflow_run_000001", relpath=RUN_SUMMARY_PATH)
    finding(project, severity="critical", execution=execution)
    with pytest.raises(TransitionError, match="bloquea Resumen"):
        go(hactors_root, project, RUN_SUMMARY_PATH, "consolidated")


def test_a_blocking_finding_outside_the_run_subtree_does_not_block_its_summary(hactors_root, project):
    summary(project, "hactors/workflow_run_000001", relpath=RUN_SUMMARY_PATH)
    finding(project, severity="critical", execution="hactors/workflow_run_000002")
    assert go(hactors_root, project, RUN_SUMMARY_PATH, "consolidated")[2] == "in-progress"


def test_closing_a_workflow_checks_nothing(hactors_root, project):
    workflow(project, "closing")
    rfc(project, "draft")
    task(project, "draft")
    finding(project, severity="critical", workflow="WORKFLOW-00001")
    assert go(hactors_root, project, WORKFLOW_PATH, "closed")[2] == "closing"


# Sin propagación ni acoplamiento.


def test_closing_an_rfc_does_not_close_its_summary(hactors_root, project):
    rfc(project, "merged", actions=[])
    summary(project, RFC_PATH)
    go(hactors_root, project, RFC_PATH, "done")
    assert "status: in-progress" in (project / SUMMARY_PATH).read_text()


def test_a_transition_does_not_propagate_to_the_task(hactors_root, project):
    rfc(project, "done")
    path = task(project, "tested", rfcs=["RFC-A00001"])
    before = path.read_text()
    go(hactors_root, project, RFC_PATH, "deprecated")
    assert path.read_text() == before


def test_a_transition_produces_no_edges(hactors_root, project):
    rfc(project, "approved", relpath=RFC_PATH, identity="RFC-A00001", superseded_by="RFC-A00002")
    manifest = project / "manifest.yaml"
    before = yaml.safe_load(manifest.read_text())
    go(hactors_root, project, RFC_PATH, "superseded")
    assert yaml.safe_load(manifest.read_text()) == before


# La CLI.


def test_the_command_reports_the_transition(hactors_root, project):
    task(project)
    result = invoke(hactors_root, "transition", "--artifact", TASK_PATH, "--to", "approved")
    assert "TASK-00001 en 'tasks/TASK-00001.md': draft → approved" in result.output


def test_the_command_reports_a_rejected_transition(hactors_root, project):
    task(project)
    result = invoke(hactors_root, "transition", "--artifact", TASK_PATH, "--to", "done", expected=1)
    assert "no admite la transición" in result.output


def test_the_command_lists_every_pending_condition(hactors_root, project):
    rfc(project, "draft")
    task(project, "tested", rfcs=["RFC-A00001"])
    finding(project, severity="critical", task="TASK-00001")
    result = invoke(hactors_root, "transition", "--artifact", TASK_PATH, "--to", "done", expected=1)
    assert "no existe" not in result.output
    assert result.output.count("tasks/TASK-00001.md") + result.output.count("FND-00001.yaml") == 2


def test_the_command_accepts_an_element_identifier(hactors_root, project):
    rfc(project, actions=[action()])
    result = invoke(
        hactors_root, "transition", "--artifact", RFC_PATH, "--to", "in-progress", "--id", "AC-00001"
    )
    assert "AC-00001 en 'rfcs/RFC-A00001.md': pending → in-progress" in result.output


def test_the_command_requires_its_two_options(hactors_root, project):
    task(project)
    invoke(hactors_root, "transition", "--to", "approved", expected=2)
    invoke(hactors_root, "transition", "--artifact", TASK_PATH, expected=2)


def test_the_command_requires_an_active_project(hactors_root):
    result = invoke(hactors_root, "transition", "--artifact", TASK_PATH, "--to", "approved", expected=1)
    assert "No hay proyecto activo." in result.output


def test_a_transition_leaves_the_project_consistent(hactors_root, project):
    invoke(hactors_root, "create-task")
    invoke(hactors_root, "transition", "--artifact", TASK_PATH, "--to", "approved")
    assert "sin inconsistencias" in invoke(hactors_root, "validate").output


# Anclaje de los vocabularios y las aristas contra sus normas.


def table_first_column(filename: Path, section: str) -> set:
    text = filename.read_text()
    body = text.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
    return {line.split("|")[1].strip().strip("`") for line in body.splitlines() if line.startswith("| `")}


def diagram(filename: Path, section: str) -> str:
    text = filename.read_text()
    body = text.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
    return body.split("```text\n", 1)[1].split("```", 1)[0]


BIDIRECTIONAL = ("↔", "⇄")
ARROWS = ("→", "↘") + BIDIRECTIONAL


def diagram_edges(body: str) -> set:
    edges, spans = set(), []
    for raw in body.splitlines():
        text = re.sub(r"\([^)]*\)", "", raw).rstrip()
        if not text.strip():
            continue
        tokens = [(match.start(), match.group()) for match in re.finditer(r"\S+", text)]
        if tokens[0][1] == "↘":
            column = tokens[0][0]
            source = next(node for start, end, node in spans if start <= column <= end)
            tokens = [(0, source), (1, "↘")] + tokens[1:]
        else:
            spans = [
                (start, start + len(value), value)
                for start, value in tokens
                if value not in ARROWS
            ]
        previous = arrow = None
        for _, value in tokens:
            if value in ARROWS:
                arrow = value
                continue
            if previous is not None and arrow is not None:
                edges.add((previous, value))
                if arrow in BIDIRECTIONAL:
                    edges.add((value, previous))
            previous, arrow = value, None
    return edges


@pytest.mark.parametrize(
    "filename, section, statuses",
    [
        (SPECS_TEMPLATES / "PLAN_TEMPLATE.md", "Estados", PLAN_STATUSES),
        (SPECS / "DECISIONS.md", "Estados de ADR", ADR_STATUSES),
        (SPECS / "TRIVIAL.md", "Estados", TRV_STATUSES),
        (SPECS_TEMPLATES / "FND_TEMPLATE.md", "Estados y transiciones", FINDING_STATES),
    ],
)
def test_the_vocabulary_matches_its_norm(filename, section, statuses):
    assert table_first_column(filename, section) == set(statuses)


def test_the_lifecycle_table_defines_the_rfc_task_and_summary_states():
    documented = table_first_column(SPECS / "LIFECYCLE.md", "Estados")
    for statuses in (RFC_STATUSES, TASK_STATUSES, SUMMARY_STATUSES):
        assert set(statuses) <= documented


def test_the_workflow_states_come_from_their_own_diagram():
    section = "WORKFLOW y acciones derivadas"
    declared = diagram_edges(diagram(SPECS / "LIFECYCLE.md", section))
    assert {node for edge in declared for node in edge} == set(WORKFLOW_STATUSES)


@pytest.mark.parametrize("family", FAMILIES, ids=lambda family: family.label)
def test_every_state_takes_part_in_an_edge(family):
    nodes = {node for edge in family.edges for node in edge}
    assert nodes == set(family.statuses)


@pytest.mark.parametrize(
    "filename, section, edges, exact",
    [
        (SPECS / "LIFECYCLE.md", "TASK", TASK_EDGES, False),
        (SPECS / "LIFECYCLE.md", "SUMMARY", SUMMARY_EDGES, True),
        (SPECS / "LIFECYCLE.md", "WORKFLOW y acciones derivadas", WORKFLOW_EDGES, False),
        (SPECS_TEMPLATES / "PLAN_TEMPLATE.md", "Estados", PLAN_EDGES, True),
        (SPECS / "TRIVIAL.md", "Estados", TRV_EDGES, True),
        (SPECS_TEMPLATES / "AC_TEMPLATE.md", "Estados", ACTION_EDGES, True),
        (SPECS_TEMPLATES / "FND_TEMPLATE.md", "Estados y transiciones", FINDING_EDGES, True),
    ],
)
def test_the_diagram_edges_are_admitted(filename, section, edges, exact):
    declared = diagram_edges(diagram(filename, section))
    assert declared
    if exact:
        assert declared == set(edges)
    else:
        assert declared <= set(edges)


def test_the_adr_edges_match_decisions():
    section = (SPECS / "DECISIONS.md").read_text().split("## Estados de ADR\n", 1)[1].split("\n## ", 1)[0]
    assert "`proposed` → `accepted`" in section
    assert "`accepted` → `superseded`" in section
    assert set(ADR_EDGES) == {
        ("proposed", "accepted"), ("proposed", "rejected"), ("accepted", "superseded")
    }


def test_the_rfc_table_edges_are_admitted():
    section = (SPECS / "LIFECYCLE.md").read_text().split("## RFC\n", 1)[1].split("\n## ", 1)[0]
    declared = set()
    for line in section.splitlines():
        if not line.startswith("|") or "→" not in line:
            continue
        source, target = [token.strip().strip("`") for token in line.split("|")[1].split("→")]
        declared.add((source, target))
    assert declared
    assert declared <= set(RFC_EDGES)


def test_the_dispositions_and_returns_are_documented():
    text = (SPECS / "LIFECYCLE.md").read_text()
    dispositions = text.split("## Rechazo, sustitución y cancelación\n", 1)[1].split("\n## ", 1)[0]
    returns = text.split("## Iteraciones y agregación\n", 1)[1].split("\n## ", 1)[0]
    for edges in (RFC_EDGES, TASK_EDGES, WORKFLOW_EDGES):
        for source, target in edges:
            if target in ("rejected", "cancelled", "superseded", "deprecated", "aborted"):
                assert f"`{source}`" in dispositions, (source, target)
                assert f"`{target}`" in dispositions
    for source in ("implemented", "tested", "under_review"):
        assert (source, "in-progress") in RFC_EDGES
        assert f"`{source}`" in returns
    assert ("validated", "in-progress") not in RFC_EDGES
    assert "La TASK no tiene arista de retorno" in returns


def test_section_17_admits_both_trivial_locations():
    text = (SPECS / "HACTORS_SYSTEM.md").read_text()
    row = next(line for line in text.splitlines() if line.startswith("| TRV |"))
    assert "del proyecto, o de la raíz de la copia" in row


def test_the_action_level_has_one_documented_exit():
    text = (SPECS / "PROJECT_STATE.md").read_text()
    rule = text.split("## Regla de consistencia entre niveles\n", 1)[1].split("\n## ", 1)[0]
    assert "solo cierra cancelándose ella misma" in rule
