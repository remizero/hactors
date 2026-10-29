from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from hactors_cli.core.plan_run import PlanRunError, create_plan_run
from hactors_cli.core.project import create_project
from hactors_cli.core.rfc_run import RfcRunError, create_rfc_run
from hactors_cli.core.state import load_state, set_active_project
from hactors_cli.core.task_run import create_task_run
from hactors_cli.core.templates import load_template, render_run_yaml
from hactors_cli.core.workflow import create_workflow


@pytest.fixture(params=["rfc_run", "plan_run"])
def run_case(request, hactors_root):
    project = create_project("test-proj", hactors_root)
    set_active_project(hactors_root, project.name)
    workflow = create_workflow(hactors_root, project.name)
    task = create_task_run(hactors_root, project.name, workflow.name)
    args = [hactors_root, project.name, workflow.name, task.name]
    if request.param == "rfc_run":
        return create_rfc_run, RfcRunError, args, task, "rfc_run", "rfc_ref", "RFC-A00001"
    rfc = create_rfc_run(*args, rfc_ref="RFC-A00001")
    args.append(rfc.name)
    return create_plan_run, PlanRunError, args, rfc, "plan_run", "plan_ref", "PLAN-00001"


def test_run_matches_template_and_preserves_source(run_case, load_yaml):
    create, _, args, parent, prefix, field, ref = run_case
    root = args[0]
    template = load_template(root, f"{prefix}_template.yaml")
    original = deepcopy(template)
    run = create(*args, **{field: ref})
    expected = deepcopy(template)
    expected["identity"].update(id=run.name, **{field: ref})
    assert run.parent == parent
    assert run.name == f"{prefix}_000001"
    assert load_yaml(run / "manifest.yaml") == expected
    assert load_template(root, f"{prefix}_template.yaml") == original
    if prefix == "rfc_run":
        assert load_state(root)["current_rfc_run"] == run.name
    else:
        assert load_state(root)["current_rfc_run"] == parent.name


def test_optional_reference_is_empty(run_case, load_yaml):
    create, _, args, _, _, field, _ = run_case
    run = create(*args)
    assert load_yaml(run / "manifest.yaml")["identity"][field] == ""


def test_defaults_come_from_template(run_case, load_yaml):
    create, _, args, _, prefix, _, _ = run_case
    path = args[0] / "specs" / "templates" / f"{prefix}_template.yaml"
    template = load_yaml(path)
    template["state"]["status"] = "pending"
    path.write_text(yaml.safe_dump(template))
    run = create(*args)
    assert load_yaml(run / "manifest.yaml")["state"] == template["state"]


def test_run_ids_are_sequential(run_case, load_yaml):
    create, _, args, _, prefix, _, _ = run_case
    first, second = create(*args), create(*args)
    assert first.name == f"{prefix}_000001"
    assert second.name == f"{prefix}_000002"
    manifest = load_yaml(args[0] / "projects" / args[1] / "manifest.yaml")
    assert manifest["counters"][prefix] == 2


def test_counters_span_parents_but_not_projects(hactors_root, load_yaml):
    for project_name in ("first", "second"):
        project = create_project(project_name, hactors_root)
        for index in (1, 2):
            workflow = create_workflow(hactors_root, project_name)
            task = create_task_run(hactors_root, project_name, workflow.name)
            rfc = create_rfc_run(hactors_root, project_name, workflow.name, task.name)
            plan = create_plan_run(hactors_root, project_name, workflow.name, task.name, rfc.name)
            assert rfc.name == f"rfc_run_{index:06d}"
            assert plan.name == f"plan_run_{index:06d}"
        counters = load_yaml(project / "manifest.yaml")["counters"]
        assert counters["rfc_run"] == counters["plan_run"] == 2
        assert counters["task"] == 0


def test_missing_template_does_not_change_manifest_or_state(run_case):
    create, error, args, parent, prefix, _, _ = run_case
    root = args[0]
    manifest = root / "projects" / args[1] / "manifest.yaml"
    before = manifest.read_bytes(), load_state(root)
    (root / "specs" / "templates" / f"{prefix}_template.yaml").unlink()
    with pytest.raises(error, match="Plantilla no encontrada"):
        create(*args)
    assert (manifest.read_bytes(), load_state(root)) == before
    assert not (parent / f"{prefix}_000001").exists()


def test_missing_parent_manifest_does_not_consume_counter(run_case):
    create, error, args, parent, _, _, _ = run_case
    manifest = args[0] / "projects" / args[1] / "manifest.yaml"
    before = manifest.read_bytes()
    (parent / "manifest.yaml").unlink()
    with pytest.raises(error, match="sin manifest"):
        create(*args)
    assert manifest.read_bytes() == before


@pytest.mark.parametrize("parent_index", [1, 2, 3])
def test_nonexistent_ancestor_does_not_consume_counter(run_case, parent_index):
    create, error, args, _, _, _, _ = run_case
    manifest = args[0] / "projects" / args[1] / "manifest.yaml"
    before = manifest.read_bytes()
    args = list(args)
    args[parent_index] = (
        "nonexistent" if parent_index == 1 else
        f"{('workflow_run' if parent_index == 2 else 'task_run')}_999999"
    )
    with pytest.raises(error, match="no encontrado"):
        create(*args)
    assert manifest.read_bytes() == before


@pytest.mark.parametrize("bad_value", ["../outside", "/tmp/outside", "wrong_000001", 42])
@pytest.mark.parametrize("parent_index", [2, 3])
def test_invalid_parent_ids_are_rejected(run_case, parent_index, bad_value):
    create, error, args, _, _, _, _ = run_case
    manifest = args[0] / "projects" / args[1] / "manifest.yaml"
    before = manifest.read_bytes()
    args = list(args)
    args[parent_index] = bad_value
    with pytest.raises(error, match="inválido"):
        create(*args)
    assert manifest.read_bytes() == before


@pytest.mark.parametrize("bad_name", ["../outside", "/tmp/outside", 42])
def test_invalid_project_context_is_rejected(run_case, bad_name):
    create, error, args, _, _, _, _ = run_case
    args = list(args)
    args[1] = bad_name
    with pytest.raises(error, match="inválido"):
        create(*args)


def test_existing_run_is_never_overwritten(run_case):
    create, error, args, parent, prefix, _, _ = run_case
    existing = parent / f"{prefix}_000001"
    existing.mkdir()
    manifest = existing / "manifest.yaml"
    manifest.write_text("preserved: true\n")
    state = load_state(args[0])
    with pytest.raises(error, match="Ya existe"):
        create(*args)
    assert manifest.read_text() == "preserved: true\n"
    assert load_state(args[0]) == state


def test_parent_symlink_cannot_escape_project(run_case, tmp_path):
    create, error, args, parent, _, _, _ = run_case
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "manifest.yaml").write_text("{}")
    link = parent.parent / ("task_run_999999" if len(args) == 4 else "rfc_run_999999")
    link.symlink_to(outside, target_is_directory=True)
    args = list(args)
    args[-1] = link.name
    with pytest.raises(error, match="fuera del directorio"):
        create(*args)
    assert list(outside.iterdir()) == [outside / "manifest.yaml"]


def test_plan_requires_existing_rfc(hactors_root):
    create_project("proj", hactors_root)
    workflow = create_workflow(hactors_root, "proj")
    task = create_task_run(hactors_root, "proj", workflow.name)
    with pytest.raises(PlanRunError, match="rfc_run no encontrado"):
        create_plan_run(hactors_root, "proj", workflow.name, task.name, "rfc_run_999999")
    with pytest.raises(PlanRunError, match="inválido"):
        create_plan_run(hactors_root, "proj", workflow.name, task.name, "../outside")


def test_render_does_not_mutate_template(hactors_root):
    template = load_template(hactors_root, "rfc_run_template.yaml")
    before = deepcopy(template)
    render_run_yaml(template, "rfc_run_000001", "RFC-A00001", "rfc_ref")
    assert template == before
