from pathlib import Path

import pytest
import yaml

from hactors_cli.core.paths import require_run_directory
from hactors_cli.core.plan_run import PlanRunError, create_plan_run
from hactors_cli.core.project import create_project
from hactors_cli.core.rfc_run import RfcRunError, create_rfc_run
from hactors_cli.core.state import StateError, load_state, set_active_run
from hactors_cli.core.task_run import TaskRunError, create_task_run
from hactors_cli.core.test_run import TestRunError as CreateTestRunError, create_test_run
from hactors_cli.core.workflow import create_workflow


def snapshot(directory):
    return {
        path.relative_to(directory).as_posix(): (
            ("link", str(path.readlink())) if path.is_symlink() else
            ("directory",) if path.is_dir() else ("file", path.read_bytes())
        )
        for path in directory.rglob("*")
    }


@pytest.fixture(params=[0, 4], ids=["initial-rfc", "deep-derived-rfc"])
def rfc_parent(hactors_root, request):
    project = create_project("proj", hactors_root)
    runs = [create_workflow(hactors_root, project.name)]
    creators = [create_task_run, create_rfc_run]
    creators += [create_plan_run, create_rfc_run] * request.param
    for create in creators:
        runs.append(create(hactors_root, project.name, runs[-1].relative_to(project).as_posix()))
    return project, runs


def test_creation_only_adds_manifest_and_updates_counter_and_selection(hactors_root, rfc_parent, load_yaml):
    project, ancestors = rfc_parent
    # A real executable reference would leave a marker if creation executed it.
    sentinel = project / "check.py"
    sentinel.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "Path(__file__).with_name('executed').write_text('unexpected execution')\n"
    )
    sentinel.chmod(0o755)
    for path in (
        project / "rfcs" / "RFC-A00001.md", project / "rfcs" / "PLAN-00001.md",
        project / "tasks" / "task_000001.md", project / "test-notes.txt",
    ):
        path.write_text(f"Preserve {path.name}\n")
    before = snapshot(hactors_root)
    expected_project = load_yaml(project / "manifest.yaml")
    expected_project["counters"]["test_run"] += 1
    parent = ancestors[-1]
    parent_path = parent.relative_to(project).as_posix()
    assert require_run_directory(hactors_root, project.name, parent_path, child_type="test_run") == parent

    run = create_test_run(hactors_root, project.name, parent_path, test_ref=sentinel.name)

    assert run == parent / "test_run_000001"
    assert load_yaml(run / "manifest.yaml") == {
        "identity": {"id": run.name, "test_ref": sentinel.name},
        "state": {"status": "", "blocked_reason": ""},
    }
    assert load_yaml(project / "manifest.yaml") == expected_project
    expected_state = {"active_project": project.name, "active_run_path": run.relative_to(project).as_posix()}
    assert load_state(hactors_root) == expected_state
    assert load_yaml(hactors_root / "projects" / ".state.yaml") == expected_state
    assert Path(expected_state["active_run_path"]).parts[1:] == tuple(p.name for p in [*ancestors, run])
    after = snapshot(hactors_root)
    added = run.relative_to(hactors_root).as_posix()
    assert after.keys() - before.keys() == {added, f"{added}/manifest.yaml"}
    assert before.keys() - after.keys() == set()
    changed = {path for path in before if before[path] != after[path]}
    assert changed == {"projects/proj/manifest.yaml", "projects/.state.yaml"}


@pytest.mark.parametrize("reference", [
    None, "", "   ", "opaque reference", "../not-a-document", "/nonexistent/check.py",
    "urn:checks:smoke#case=7", "línea: 'uno'\nsegunda # literal",
], ids=["omitted", "empty", "whitespace", "opaque", "relative", "absolute", "uri", "yaml-sensitive"])
def test_references_are_stored_verbatim_without_document_validation(hactors_root, rfc_parent, load_yaml, reference):
    project, runs = rfc_parent
    kwargs = {} if reference is None else {"test_ref": reference}
    run = create_test_run(hactors_root, project.name, runs[-1].relative_to(project).as_posix(), **kwargs)
    assert load_yaml(run / "manifest.yaml")["identity"] == {
        "id": run.name, "test_ref": "" if reference is None else reference,
    }
    assert list(run.iterdir()) == [run / "manifest.yaml"]
    assert list((project / "rfcs").iterdir()) == []


def test_sibling_tests_coexist_with_plans_and_do_not_interrupt_recursion(hactors_root, rfc_parent, load_yaml):
    project, runs = rfc_parent
    parent = runs[-1]
    path = parent.relative_to(project).as_posix()
    counters = load_yaml(project / "manifest.yaml")["counters"].copy()
    originals = {run / "manifest.yaml": (run / "manifest.yaml").read_bytes() for run in runs}
    first = create_test_run(hactors_root, project.name, path)
    plan = create_plan_run(hactors_root, project.name, path)
    second = create_test_run(hactors_root, project.name, path)
    other_plan = create_plan_run(hactors_root, project.name, path)
    derived = create_rfc_run(hactors_root, project.name, plan.relative_to(project).as_posix())
    third = create_test_run(hactors_root, project.name, derived.relative_to(project).as_posix())
    assert [run.name for run in (first, second, third)] == [
        "test_run_000001", "test_run_000002", "test_run_000003",
    ]
    assert first.parent == second.parent == plan.parent == other_plan.parent == parent
    assert third.parent == derived and derived.parent == plan
    assert plan.name == f"plan_run_{counters['plan_run'] + 1:06d}"
    assert other_plan.name == f"plan_run_{counters['plan_run'] + 2:06d}"
    counters["plan_run"] += 2
    counters["rfc_run"] += 1
    counters["test_run"] += 3
    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    assert all(path.read_bytes() == content for path, content in originals.items())
    before = snapshot(project)
    for run in (second, plan, third, first, other_plan):
        set_active_run(hactors_root, project.name, run.relative_to(project).as_posix())
        assert load_state(hactors_root) == {
            "active_project": project.name, "active_run_path": run.relative_to(project).as_posix(),
        }
    assert snapshot(project) == before


@pytest.mark.parametrize("child_type,create,error", [
    ("workflow_run", None, None),
    ("task_run", create_task_run, TaskRunError),
    ("rfc_run", create_rfc_run, RfcRunError),
    ("plan_run", create_plan_run, PlanRunError),
    ("test_run", create_test_run, CreateTestRunError),
])
def test_test_run_rejects_every_child_without_falling_back(hactors_root, rfc_parent, child_type, create, error):
    project, runs = rfc_parent
    run = create_test_run(hactors_root, project.name, runs[-1].relative_to(project).as_posix())
    path = run.relative_to(project).as_posix()
    before = snapshot(hactors_root)
    with pytest.raises(ValueError, match="No se puede crear"):
        require_run_directory(hactors_root, project.name, path, child_type=child_type)
    # Workflows are created at project level and have no parent_run_path argument.
    if create is not None:
        with pytest.raises(error, match="No se puede crear"):
            create(hactors_root, project.name, path)
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("child_type", ["workflow_run", "task_run", "rfc_run", "plan_run", "test_run"])
def test_existing_child_inside_test_cannot_be_selected(hactors_root, rfc_parent, child_type, load_yaml):
    project, runs = rfc_parent
    parent = runs[-1].relative_to(project).as_posix()
    plan = create_plan_run(hactors_root, project.name, parent)
    test = create_test_run(hactors_root, project.name, parent)
    sources = {"workflow_run": runs[0], "task_run": runs[1], "rfc_run": runs[2], "plan_run": plan, "test_run": test}
    source = sources[child_type]
    child = test / f"{child_type}_999999"
    child.mkdir()
    data = load_yaml(source / "manifest.yaml")
    if child_type == "workflow_run":
        data = {child.name: data[source.name]}
        data[child.name]["identity"]["id"] = child.name
    else:
        data["identity"]["id"] = child.name
    (child / "manifest.yaml").write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)
    path = child.relative_to(project).as_posix()
    with pytest.raises(ValueError, match="Jerarquía inválida"):
        require_run_directory(hactors_root, project.name, path)
    with pytest.raises(StateError, match="Jerarquía inválida"):
        set_active_run(hactors_root, project.name, path)
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("parent_type", ["workflow_run", "task_run", "plan_run", "test_run"])
def test_existing_test_under_incompatible_parent_cannot_be_selected(hactors_root, rfc_parent, parent_type):
    project, runs = rfc_parent
    path = runs[-1].relative_to(project).as_posix()
    plan = create_plan_run(hactors_root, project.name, path)
    test = create_test_run(hactors_root, project.name, path)
    parent = {"workflow_run": runs[0], "task_run": runs[1], "plan_run": plan, "test_run": test}[parent_type]
    misplaced = parent / "test_run_999999"
    misplaced.mkdir()
    (misplaced / "manifest.yaml").write_text(yaml.safe_dump({
        "identity": {"id": misplaced.name, "test_ref": ""},
        "state": {"status": "", "blocked_reason": ""},
    }))
    before = snapshot(hactors_root)
    with pytest.raises(ValueError, match="Jerarquía inválida"):
        require_run_directory(hactors_root, project.name, misplaced.relative_to(project).as_posix())
    with pytest.raises(StateError, match="Jerarquía inválida"):
        set_active_run(hactors_root, project.name, misplaced.relative_to(project).as_posix())
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("missing", [False, True], ids=["stale-counter", "legacy-missing-counter"])
def test_preflight_collision_preserves_existing_test_and_can_recover(hactors_root, rfc_parent, load_yaml, missing):
    project, runs = rfc_parent
    path = runs[-1].relative_to(project).as_posix()
    first = create_test_run(hactors_root, project.name, path, test_ref="keep this reference")
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    if missing:
        data["counters"].pop("test_run")
    else:
        data["counters"]["test_run"] = 0
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)
    with pytest.raises(CreateTestRunError, match="Ya existe"):
        create_test_run(hactors_root, project.name, path)
    assert snapshot(hactors_root) == before
    data["counters"]["test_run"] = 1
    manifest.write_text(yaml.safe_dump(data))
    second = create_test_run(hactors_root, project.name, path)
    assert second.name == "test_run_000002"
    assert load_yaml(first / "manifest.yaml")["identity"]["test_ref"] == "keep this reference"
    data["counters"]["test_run"] = 2
    assert load_yaml(manifest) == data
