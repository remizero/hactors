from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from hactors_cli.core.paths import require_project_directory, require_run_directory
from hactors_cli.core.project import create_project
from hactors_cli.core.state import load_state, set_active_project
from hactors_cli.core.task_run import TaskRunError, create_task_run
from hactors_cli.core.workflow import WorkflowError, create_workflow


def snapshot(directory):
    return {
        path.relative_to(directory).as_posix(): path.read_bytes() if path.is_file() else None
        for path in directory.rglob("*")
    }


@pytest.fixture(params=["workflow_run", "task_run"])
def run_case(request, hactors_root):
    project = create_project("test-proj", hactors_root)
    if request.param == "workflow_run":
        return create_workflow, WorkflowError, [hactors_root, project.name], project / "hactors", "workflow_run"
    workflow = create_workflow(hactors_root, project.name)
    return (
        create_task_run, TaskRunError,
        [hactors_root, project.name, workflow.relative_to(project).as_posix()], workflow, "task_run",
    )


def template_path(root, prefix):
    filename = "workflow_run_manifest_template.yaml" if prefix == "workflow_run" else "task_run_template.yaml"
    return root / "specs" / "templates" / filename


def test_run_matches_template_and_preserves_source(run_case, load_yaml):
    create, _, args, parent, prefix = run_case
    path = template_path(args[0], prefix)
    original = path.read_bytes()
    expected = deepcopy(load_yaml(path))
    options = {"task_ref": "task_000001"} if prefix == "workflow_run" else {}
    run = create(*args, **options)
    expected["identity"].update(id=run.name, **options)
    expected = {run.name: expected} if prefix == "workflow_run" else expected
    assert run.parent == parent
    assert run.name == f"{prefix}_000001"
    assert run.is_dir()
    assert load_yaml(run / "manifest.yaml") == expected
    assert path.read_bytes() == original
    project = args[0] / "projects" / args[1]
    assert load_state(args[0]) == {
        "active_project": args[1], "active_run_path": run.relative_to(project).as_posix(),
    }
    assert require_project_directory(args[0], args[1]) == project
    assert require_run_directory(args[0], args[1], run.relative_to(project).as_posix()) == run


def test_sequential_runs_only_increment_their_own_counter(run_case, load_yaml):
    create, _, args, _, prefix = run_case
    manifest = args[0] / "projects" / args[1] / "manifest.yaml"
    expected = load_yaml(manifest)["counters"].copy()
    first, second = create(*args), create(*args)
    assert first.name == f"{prefix}_000001"
    assert second.name == f"{prefix}_000002"
    expected[prefix] += 2
    assert load_yaml(manifest)["counters"] == expected


def test_defaults_come_from_template(run_case, load_yaml):
    create, _, args, _, prefix = run_case
    path = template_path(args[0], prefix)
    template = load_yaml(path)
    state_key = "global_state" if prefix == "workflow_run" else "state"
    template[state_key]["status"] = "pending"
    path.write_text(yaml.safe_dump(template))
    original = path.read_bytes()
    run = create(*args)
    body = load_yaml(run / "manifest.yaml")
    if prefix == "workflow_run":
        body = body[run.name]
        assert body["identity"]["task_ref"] == ""
    else:
        assert body["identity"] == {"id": run.name}
    assert body[state_key] == template[state_key]
    assert path.read_bytes() == original


def test_explicit_core_creation_updates_both_state_keys(run_case):
    create, _, args, _, _ = run_case
    create_project("other", args[0])
    set_active_project(args[0], "other")
    run = create(*args)
    project = args[0] / "projects" / args[1]
    assert load_state(args[0]) == {
        "active_project": args[1], "active_run_path": run.relative_to(project).as_posix(),
    }


def test_missing_template_has_no_side_effects(run_case):
    create, error, args, _, prefix = run_case
    template_path(args[0], prefix).unlink()
    before = snapshot(args[0] / "projects")
    with pytest.raises(error, match="Plantilla no encontrada"):
        create(*args)
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("collision", ["directory", "file"])
def test_existing_run_is_not_overwritten_or_counted(run_case, collision):
    create, error, args, parent, prefix = run_case
    existing = parent / f"{prefix}_000001"
    if collision == "directory":
        existing.mkdir()
        (existing / "manifest.yaml").write_text("preserved: true\n")
    else:
        existing.write_text("preserved file\n")
    before = snapshot(args[0] / "projects")
    with pytest.raises(error, match="Ya existe"):
        create(*args)
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("problem", ["missing", "missing-manifest", "wrong-project", "malformed"])
def test_invalid_project_has_no_side_effects(run_case, problem, load_yaml):
    create, error, args, _, _ = run_case
    args = list(args)
    project = args[0] / "projects" / args[1]
    manifest = project / "manifest.yaml"
    if problem == "missing":
        args[1] = "nonexistent"
    elif problem == "missing-manifest":
        manifest.unlink()
    elif problem == "wrong-project":
        data = load_yaml(manifest)
        data["project"] = "other"
        manifest.write_text(yaml.safe_dump(data))
    else:
        manifest.write_text("project: [broken")
    before = snapshot(args[0] / "projects")
    with pytest.raises(error) as caught:
        create(*args)
    assert str(caught.value).strip()
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("parent_path", [
    "hactors/workflow_run_999999", "workflow_run_000001",
    "hactors/workflow_run_000001/../workflow_run_000001", 42,
])
def test_task_requires_a_complete_existing_parent_path(hactors_root: Path, parent_path):
    create_project("proj", hactors_root)
    create_workflow(hactors_root, "proj")
    before = snapshot(hactors_root / "projects")
    with pytest.raises(TaskRunError):
        create_task_run(hactors_root, "proj", parent_path)
    assert snapshot(hactors_root / "projects") == before


def test_task_requires_workflow_manifest(hactors_root):
    project = create_project("proj", hactors_root)
    workflow = create_workflow(hactors_root, project.name)
    (workflow / "manifest.yaml").unlink()
    before = snapshot(hactors_root / "projects")
    with pytest.raises(TaskRunError, match="manifest"):
        create_task_run(hactors_root, project.name, workflow.relative_to(project).as_posix())
    assert snapshot(hactors_root / "projects") == before


def test_task_counters_span_workflows_not_projects(hactors_root, load_yaml):
    for name in ("first", "second"):
        project = create_project(name, hactors_root)
        for index in (1, 2):
            workflow = create_workflow(hactors_root, name)
            task = create_task_run(hactors_root, name, workflow.relative_to(project).as_posix())
            assert task.parent == workflow
            assert task.name == f"task_run_{index:06d}"
        assert load_yaml(project / "manifest.yaml")["counters"] == {
            "task": 0, "workflow_run": 2, "task_run": 2, "rfc_run": 0, "plan_run": 0,
            "test_run": 0, "harness_run": 0, "evidence": 0,
        }


@pytest.mark.parametrize("prefix", ["workflow_run", "task_run"])
def test_missing_counter_is_added_without_rewriting_existing_runs(hactors_root, load_yaml, prefix):
    project = create_project("proj", hactors_root)
    workflow = create_workflow(hactors_root, project.name) if prefix == "task_run" else None
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"].pop(prefix)
    manifest.write_text(yaml.safe_dump(data))
    if workflow is None:
        run = create_workflow(hactors_root, project.name)
    else:
        original = (workflow / "manifest.yaml").read_bytes()
        run = create_task_run(hactors_root, project.name, workflow.relative_to(project).as_posix())
        assert (workflow / "manifest.yaml").read_bytes() == original
    assert run.name == f"{prefix}_000001"
    assert load_yaml(manifest)["counters"][prefix] == 1
