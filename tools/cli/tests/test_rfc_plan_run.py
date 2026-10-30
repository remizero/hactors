from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from hactors_cli.core.harness_run import HarnessRunError, create_harness_run
from hactors_cli.core.paths import require_run_directory
from hactors_cli.core.plan_run import PlanRunError, create_plan_run
from hactors_cli.core.project import create_project
from hactors_cli.core.rfc_run import RfcRunError, create_rfc_run
from hactors_cli.core.state import load_state, select_parent_run, set_active_run
from hactors_cli.core.task_run import TaskRunError, create_task_run
from hactors_cli.core.templates import load_template, render_run_yaml
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


@pytest.fixture(params=["rfc_run", "plan_run", "test_run", "harness_run"])
def run_case(request, hactors_root):
    project = create_project("test-proj", hactors_root)
    workflow = create_workflow(hactors_root, project.name)
    task = create_task_run(hactors_root, project.name, workflow.relative_to(project).as_posix())
    args = [hactors_root, project.name, task.relative_to(project).as_posix()]
    if request.param == "rfc_run":
        return create_rfc_run, RfcRunError, args, task, "rfc_run", "rfc_ref", "RFC-A00001"
    rfc = create_rfc_run(*args, rfc_ref="RFC-A00001")
    args[2] = rfc.relative_to(project).as_posix()
    if request.param == "test_run":
        return create_test_run, CreateTestRunError, args, rfc, "test_run", "test_ref", "opaque test reference"
    if request.param == "harness_run":
        test = create_test_run(*args)
        args[2] = test.relative_to(project).as_posix()
        return create_harness_run, HarnessRunError, args, test, "harness_run", "harness_ref", "HRN-00001@v1"
    return create_plan_run, PlanRunError, args, rfc, "plan_run", "plan_ref", "PLAN-00001"


def test_run_matches_template_and_preserves_source(run_case, load_yaml):
    create, _, args, parent, prefix, field, ref = run_case
    root = args[0]
    source = root / "specs" / "templates" / f"{prefix}_template.yaml"
    original = source.read_bytes()
    expected = deepcopy(load_template(root, source.name))
    run = create(*args, **{field: ref})
    expected["identity"].update(id=run.name, **{field: ref})
    assert run.parent == parent
    assert run.name == f"{prefix}_000001"
    assert load_yaml(run / "manifest.yaml") == expected
    assert source.read_bytes() == original
    assert load_state(root) == {
        "active_project": args[1], "active_run_path": f"{args[2]}/{run.name}",
    }


def test_optional_reference_is_empty(run_case, load_yaml):
    create, _, args, _, _, field, _ = run_case
    run = create(*args)
    assert load_yaml(run / "manifest.yaml")["identity"][field] == ""


def test_defaults_come_from_template(run_case, load_yaml):
    create, _, args, _, prefix, _, _ = run_case
    path = args[0] / "specs" / "templates" / f"{prefix}_template.yaml"
    template = load_yaml(path)
    template["state"].update(status="pending", blocked_reason="waiting for review")
    path.write_text(yaml.safe_dump(template))
    before = path.read_bytes()
    run = create(*args)
    assert load_yaml(run / "manifest.yaml")["state"] == template["state"]
    assert path.read_bytes() == before


def test_run_ids_are_sequential_and_counters_independent(run_case, load_yaml):
    create, _, args, _, prefix, _, _ = run_case
    manifest = args[0] / "projects" / args[1] / "manifest.yaml"
    expected = load_yaml(manifest)["counters"].copy()
    first, second = create(*args), create(*args)
    assert first.name == f"{prefix}_000001"
    assert second.name == f"{prefix}_000002"
    expected[prefix] += 2
    assert load_yaml(manifest)["counters"] == expected


def test_core_uses_explicit_parent_even_in_another_project(run_case):
    create, _, args, parent, _, _, _ = run_case
    other = create_project("other", args[0])
    create_workflow(args[0], other.name)
    before = snapshot(other)
    run = create(*args)
    assert run.parent == parent
    assert load_state(args[0]) == {
        "active_project": args[1], "active_run_path": f"{args[2]}/{run.name}",
    }
    assert snapshot(other) == before


def test_counters_span_parents_but_not_projects(hactors_root, load_yaml):
    for project_name in ("first", "second"):
        project = create_project(project_name, hactors_root)
        for index in (1, 2):
            workflow = create_workflow(hactors_root, project_name)
            task = create_task_run(hactors_root, project_name, workflow.relative_to(project).as_posix())
            rfc = create_rfc_run(hactors_root, project_name, task.relative_to(project).as_posix())
            plan = create_plan_run(hactors_root, project_name, rfc.relative_to(project).as_posix())
            test = create_test_run(hactors_root, project_name, rfc.relative_to(project).as_posix())
            harness = create_harness_run(hactors_root, project_name, test.relative_to(project).as_posix())
            assert rfc.name == f"rfc_run_{index:06d}"
            assert plan.name == f"plan_run_{index:06d}"
            assert test.name == f"test_run_{index:06d}"
            assert harness.name == f"harness_run_{index:06d}"
            assert harness.parent == test
        assert load_yaml(project / "manifest.yaml")["counters"] == {
            "task": 0, "workflow_run": 2, "task_run": 2, "rfc_run": 2, "plan_run": 2,
            "test_run": 2, "harness_run": 2, "evidence": 0, "finding": 0, "adr": 0,
        }


def test_missing_template_does_not_change_manifest_state_or_directories(run_case):
    create, error, args, _, prefix, _, _ = run_case
    (args[0] / "specs" / "templates" / f"{prefix}_template.yaml").unlink()
    before = snapshot(args[0] / "projects")
    with pytest.raises(error, match="Plantilla no encontrada"):
        create(*args)
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("level", ["project", "workflow", "parent"])
@pytest.mark.parametrize("problem", ["missing", "malformed", "non-mapping", "wrong-id", "non-mapping-identity"])
def test_invalid_ancestor_manifest_has_no_side_effects(run_case, level, problem, load_yaml):
    create, error, args, parent, _, _, _ = run_case
    project = args[0] / "projects" / args[1]
    ancestor = {
        "project": project, "workflow": project / Path(args[2]).parts[0] / Path(args[2]).parts[1],
        "parent": parent,
    }[level]
    manifest = ancestor / "manifest.yaml"
    if problem == "missing":
        manifest.unlink()
    elif problem in ("malformed", "non-mapping"):
        manifest.write_text("identity: [broken" if problem == "malformed" else "[]\n")
    else:
        data = load_yaml(manifest)
        if level == "project":
            data["project"] = "other" if problem == "wrong-id" else []
        else:
            body = data[ancestor.name] if level == "workflow" else data
            if problem == "wrong-id":
                body["identity"]["id"] = "wrong_999999"
            else:
                body["identity"] = []
        manifest.write_text(yaml.safe_dump(data))
    before = snapshot(args[0] / "projects")
    with pytest.raises(error, match="[Mm]anifest"):
        create(*args)
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("component", ["project", "workflow", "parent"])
def test_nonexistent_ancestor_has_no_side_effects(run_case, component):
    create, error, args, _, _, _, _ = run_case
    args = list(args)
    if component == "project":
        args[1] = "nonexistent"
    else:
        parts = list(Path(args[2]).parts)
        index = 1 if component == "workflow" else -1
        parts[index] = parts[index].rsplit("_", 1)[0] + "_999999"
        args[2] = "/".join(parts)
    before = snapshot(args[0] / "projects")
    with pytest.raises(error):
        create(*args)
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("case", [
    "outside", "absolute", "bare-id", "wrong-id", "number", "none", "empty", "hactors-only",
    "dot", "dotdot", "backslash", "double-slash", "trailing-slash", "file", "short-id", "suffix",
])
def test_invalid_parent_paths_are_rejected(run_case, case):
    create, error, args, _, _, _, _ = run_case
    valid = args[2]
    bad_value = {
        "outside": "../outside", "absolute": "/tmp/outside", "bare-id": "workflow_run_000001",
        "wrong-id": "wrong_000001", "number": 42, "none": None, "empty": "", "hactors-only": "hactors",
        "dot": valid.replace("hactors/", "hactors/./", 1),
        "dotdot": valid.replace("hactors/", "hactors/../hactors/", 1),
        "backslash": valid.replace("/", "\\"), "double-slash": valid.replace("/", "//", 1),
        "trailing-slash": valid + "/", "file": valid + "/manifest.yaml",
        "short-id": valid.replace("workflow_run_000001", "workflow_run_1"),
        "suffix": valid + "/unknown_000001",
    }[case]
    before = snapshot(args[0] / "projects")
    with pytest.raises(error):
        create(*args[:2], bad_value)
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("bad_name", ["../outside", "/tmp/outside", 42])
def test_invalid_project_context_is_rejected(run_case, bad_name):
    create, error, args, _, _, _, _ = run_case
    before = snapshot(args[0] / "projects")
    with pytest.raises(error):
        create(args[0], bad_name, args[2])
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("collision", ["directory", "file", "symlink", "dangling-symlink"])
def test_existing_run_is_never_overwritten_or_counted(run_case, collision, tmp_path):
    create, error, args, parent, prefix, _, _ = run_case
    existing = parent / f"{prefix}_000001"
    target = tmp_path / "collision-target"
    target.mkdir()
    if collision == "directory":
        existing.mkdir()
        (existing / "manifest.yaml").write_text("preserved: true\n")
    elif collision == "file":
        existing.write_text("preserved file\n")
    elif collision == "symlink":
        (target / "manifest.yaml").write_text("preserved target\n")
        existing.symlink_to(target, target_is_directory=True)
    else:
        existing.symlink_to(target / "missing", target_is_directory=True)
    before = snapshot(args[0] / "projects"), snapshot(target)
    with pytest.raises(error, match="Ya existe"):
        create(*args)
    assert (snapshot(args[0] / "projects"), snapshot(target)) == before


@pytest.mark.parametrize("external", [False, True], ids=["internal", "external"])
@pytest.mark.parametrize("location", ["parent", "ancestor", "parent-manifest", "ancestor-manifest"])
def test_parent_chain_symlink_is_rejected_without_writing_target(run_case, tmp_path, external, location):
    create, error, args, parent, _, _, _ = run_case
    project = args[0] / "projects" / args[1]
    node = project / "hactors" / Path(args[2]).parts[1] if location.startswith("ancestor") else parent
    if location.endswith("manifest"):
        node /= "manifest.yaml"
    is_directory = node.is_dir()
    target = (tmp_path if external else project) / "original-node"
    node.rename(target)
    node.symlink_to(target, target_is_directory=is_directory)
    before = snapshot(tmp_path)
    with pytest.raises(error):
        create(*args)
    assert snapshot(tmp_path) == before


def test_new_counter_added_without_rewriting_ancestors(run_case, load_yaml):
    create, _, args, parent, prefix, _, _ = run_case
    manifest = args[0] / "projects" / args[1] / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"].pop(prefix)
    manifest.write_text(yaml.safe_dump(data))
    before = (parent / "manifest.yaml").read_bytes()
    run = create(*args)
    assert run.name == f"{prefix}_000001"
    data["counters"][prefix] = 1
    assert load_yaml(manifest) == data
    assert (parent / "manifest.yaml").read_bytes() == before


@pytest.mark.parametrize("depth", [6, 10])
def test_recursive_chain_preserves_all_ancestors_and_global_counters(hactors_root, load_yaml, depth):
    project = create_project("proj", hactors_root)
    workflow = create_workflow(hactors_root, project.name, task_ref="TASK-00001")
    runs = [workflow, create_task_run(hactors_root, project.name, workflow.relative_to(project).as_posix())]
    originals = {run / "manifest.yaml": (run / "manifest.yaml").read_bytes() for run in runs}
    templates = {name: load_template(hactors_root, f"{name}_template.yaml") for name in ("rfc_run", "plan_run")}
    expected_counters = {
        "task": 0, "workflow_run": 1, "task_run": 1, "rfc_run": 0, "plan_run": 0,
        "test_run": 0, "harness_run": 0, "evidence": 0, "finding": 0, "adr": 0,
    }
    for current_depth in range(2, depth + 1):
        is_rfc = current_depth % 2 == 0
        prefix, field, ref = ("rfc_run", "rfc_ref", "RFC-A00001") if is_rfc else ("plan_run", "plan_ref", "PLAN-00001")
        create = create_rfc_run if is_rfc else create_plan_run
        parent = runs[-1]
        parent_path = parent.relative_to(project).as_posix()
        assert require_run_directory(hactors_root, project.name, parent_path, child_type=prefix) == parent
        run = create(hactors_root, project.name, parent_path, **{field: ref})
        runs.append(run)
        expected_counters[prefix] += 1
        expected = deepcopy(templates[prefix])
        expected["identity"].update(id=run.name, **{field: ref})
        assert load_yaml(run / "manifest.yaml") == expected
        assert run.name == f"{prefix}_{expected_counters[prefix]:06d}"
        path = run.relative_to(project).as_posix()
        assert Path(path).parts[1:] == tuple(ancestor.name for ancestor in runs)
        assert len(Path(path).parts) - 2 == current_depth
        assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": path}
        assert load_yaml(project / "manifest.yaml")["counters"] == expected_counters
        assert all(file.read_bytes() == content for file, content in originals.items())
        originals[run / "manifest.yaml"] = (run / "manifest.yaml").read_bytes()

    first_plan = runs[3]
    set_active_run(hactors_root, project.name, first_plan.relative_to(project).as_posix())
    sibling = create_rfc_run(hactors_root, project.name, load_state(hactors_root)["active_run_path"])
    expected_counters["rfc_run"] += 1
    assert sibling.parent == runs[4].parent == first_plan
    assert sibling.name == f"rfc_run_{expected_counters['rfc_run']:06d}"
    assert select_parent_run(hactors_root) == first_plan.relative_to(project).as_posix()
    set_active_run(hactors_root, project.name, runs[-1].relative_to(project).as_posix())
    assert load_state(hactors_root)["active_run_path"] == runs[-1].relative_to(project).as_posix()
    assert load_yaml(project / "manifest.yaml")["counters"] == expected_counters
    assert all(file.read_bytes() == content for file, content in originals.items())
    assert list((project / "rfcs").iterdir()) == []
    assert list((project / "tasks").iterdir()) == []
    for prefix, template in templates.items():
        assert load_template(hactors_root, f"{prefix}_template.yaml") == template


@pytest.mark.parametrize("create,error,child_type,parent_index", [
    (create_task_run, TaskRunError, "task_run", 1),
    (create_task_run, TaskRunError, "task_run", 3),
    (create_rfc_run, RfcRunError, "rfc_run", 0),
    (create_rfc_run, RfcRunError, "rfc_run", 2),
    (create_plan_run, PlanRunError, "plan_run", 0),
    (create_plan_run, PlanRunError, "plan_run", 1),
    (create_plan_run, PlanRunError, "plan_run", 3),
    (create_test_run, CreateTestRunError, "test_run", 0),
    (create_test_run, CreateTestRunError, "test_run", 1),
    (create_test_run, CreateTestRunError, "test_run", 3),
    (create_harness_run, HarnessRunError, "harness_run", 0),
    (create_harness_run, HarnessRunError, "harness_run", 1),
    (create_harness_run, HarnessRunError, "harness_run", 2),
    (create_harness_run, HarnessRunError, "harness_run", 3),
])
def test_incompatible_parent_never_falls_back_to_ancestor(
    hactors_root, create, error, child_type, parent_index,
):
    project = create_project("proj", hactors_root)
    runs = [create_workflow(hactors_root, project.name)]
    for create_child in (create_task_run, create_rfc_run, create_plan_run):
        runs.append(create_child(hactors_root, project.name, runs[-1].relative_to(project).as_posix()))
    path = runs[parent_index].relative_to(project).as_posix()
    set_active_run(hactors_root, project.name, path)
    before = snapshot(hactors_root / "projects")
    with pytest.raises(ValueError):
        require_run_directory(hactors_root, project.name, path, child_type=child_type)
    with pytest.raises(error, match="No se puede crear"):
        create(hactors_root, project.name, path)
    assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("run_case", ["rfc_run", "plan_run"], indirect=True)
@pytest.mark.parametrize("missing", [False, True], ids=["stale", "missing"])
def test_next_id_cannot_repeat_an_ancestor_before_any_write(run_case, load_yaml, missing):
    create, error, args, _, prefix, _, _ = run_case
    first = create(*args)
    project = args[0] / "projects" / args[1]
    create_child = create_plan_run if prefix == "rfc_run" else create_rfc_run
    parent = create_child(args[0], args[1], first.relative_to(project).as_posix())
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    if missing:
        data["counters"].pop(prefix)
    else:
        data["counters"][prefix] = 0
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(args[0] / "projects")
    with pytest.raises(error, match="ancestral repetido"):
        create(args[0], args[1], parent.relative_to(project).as_posix())
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("value", [-1, True, False, 1.5, "1", None, [], {}])
def test_invalid_counter_is_rejected_before_any_write(run_case, load_yaml, value):
    create, error, args, _, prefix, _, _ = run_case
    manifest = args[0] / "projects" / args[1] / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"][prefix] = value
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(args[0] / "projects")
    with pytest.raises(error, match="Contador inválido"):
        create(*args)
    assert snapshot(args[0] / "projects") == before


@pytest.mark.parametrize("value", [None, [], "invalid", 1, False])
def test_invalid_counters_mapping_is_rejected_before_any_write(run_case, load_yaml, value):
    create, error, args, _, _, _, _ = run_case
    manifest = args[0] / "projects" / args[1] / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"] = value
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(args[0])
    with pytest.raises(error, match="Contadores inválidos"):
        create(*args)
    assert snapshot(args[0]) == before


@pytest.mark.parametrize("content", ["identity: [broken", "[]\n", "null\n", "42\n"])
def test_invalid_template_is_rejected_before_any_write(run_case, content):
    create, error, args, _, prefix, _, _ = run_case
    source = args[0] / "specs" / "templates" / f"{prefix}_template.yaml"
    source.write_text(content)
    before = snapshot(args[0])
    with pytest.raises(error):
        create(*args)
    assert snapshot(args[0]) == before


def test_render_does_not_mutate_template(hactors_root):
    template = load_template(hactors_root, "rfc_run_template.yaml")
    before = deepcopy(template)
    render_run_yaml(template, "rfc_run_000001", "RFC-A00001", "rfc_ref")
    assert template == before
