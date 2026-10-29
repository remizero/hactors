from pathlib import Path

import pytest
import yaml

from hactors_cli.core.paths import require_project_directory, require_run_directory
from hactors_cli.core.plan_run import create_plan_run
from hactors_cli.core.project import create_project
from hactors_cli.core.rfc_run import create_rfc_run
from hactors_cli.core.state import (
    NoActiveProjectError,
    NoActiveRunError,
    StateError,
    load_state,
    require_active_project,
    require_active_run_path,
    save_state,
    select_parent_run,
    set_active_project,
    set_active_run,
)
from hactors_cli.core.task_run import create_task_run
from hactors_cli.core.workflow import create_workflow


def snapshot(directory):
    return {
        path.relative_to(directory).as_posix(): (
            ("link", str(path.readlink())) if path.is_symlink() else
            ("directory",) if path.is_dir() else ("file", path.read_bytes())
        )
        for path in directory.rglob("*")
    }


@pytest.fixture
def selected_chain(hactors_root):
    project = create_project("proj", hactors_root)
    runs = [create_workflow(hactors_root, project.name)]
    for create in (
        create_task_run, create_rfc_run, create_plan_run,
        create_rfc_run, create_plan_run, create_rfc_run,
    ):
        runs.append(create(hactors_root, project.name, runs[-1].relative_to(project).as_posix()))
    return project, runs


class TestLoadState:
    def test_returns_only_new_defaults_when_no_file(self, hactors_root: Path):
        assert load_state(hactors_root) == {"active_project": "", "active_run_path": ""}
        assert not (hactors_root / "projects" / ".state.yaml").exists()

    def test_round_trip_full_path(self, hactors_root, selected_chain, load_yaml):
        project, runs = selected_chain
        expected = {
            "active_project": project.name,
            "active_run_path": runs[-1].relative_to(project).as_posix(),
        }
        save_state(hactors_root, expected)
        assert load_state(hactors_root) == expected
        assert load_yaml(hactors_root / "projects" / ".state.yaml") == expected

    def test_absent_run_field_is_empty(self, hactors_root):
        create_project("proj", hactors_root)
        (hactors_root / "projects" / ".state.yaml").write_text("active_project: proj\n")
        assert load_state(hactors_root) == {"active_project": "proj", "active_run_path": ""}

    @pytest.mark.parametrize("field", [
        "current_workflow_run", "current_task_run", "current_rfc_run",
    ])
    @pytest.mark.parametrize("value", ["", "old_000001"])
    def test_legacy_fields_rejected_even_when_empty(self, hactors_root, field, value):
        path = hactors_root / "projects" / ".state.yaml"
        path.write_text(yaml.safe_dump({
            "active_project": "proj", "active_run_path": "", field: value,
        }))
        before = snapshot(hactors_root / "projects")
        with pytest.raises(StateError) as error:
            load_state(hactors_root)
        assert "use-project" in str(error.value)
        assert "use-run" in str(error.value)
        assert snapshot(hactors_root / "projects") == before

    @pytest.mark.parametrize("content", [
        "active_project: [unterminated", "[]\n", "42\n", "null\n", "text\n",
        "active_project: null\n", "active_project: 42\n", "active_project: false\n",
        "active_project: []\n", "active_project: {}\n",
        "active_project: proj\nactive_run_path: null\n",
        "active_project: proj\nactive_run_path: 42\n",
        "active_project: proj\nactive_run_path: false\n",
        "active_project: proj\nactive_run_path: []\n",
        "active_project: proj\nactive_run_path: {}\n",
        "active_project: ''\nactive_run_path: hactors/workflow_run_000001\n",
    ])
    def test_corrupt_state_is_a_readable_error_without_mutation(self, hactors_root, content):
        path = hactors_root / "projects" / ".state.yaml"
        path.write_text(content)
        before = snapshot(hactors_root / "projects")
        with pytest.raises(StateError) as error:
            load_state(hactors_root)
        assert str(error.value).strip()
        assert snapshot(hactors_root / "projects") == before


class TestActiveSelection:
    def test_requires_project_and_run(self, hactors_root):
        with pytest.raises(NoActiveProjectError, match="No hay proyecto activo"):
            require_active_project(hactors_root)
        create_project("proj", hactors_root)
        set_active_project(hactors_root, "proj")
        assert require_active_project(hactors_root) == "proj"
        with pytest.raises(NoActiveRunError, match="No hay instancia activa"):
            require_active_run_path(hactors_root)
        before = snapshot(hactors_root / "projects")
        with pytest.raises(NoActiveRunError, match="No hay instancia activa"):
            select_parent_run(hactors_root)
        assert snapshot(hactors_root / "projects") == before

    def test_parent_removes_one_component_preserving_repeated_types(self, hactors_root, selected_chain):
        project, runs = selected_chain
        before = snapshot(project)
        expected_paths = [run.relative_to(project).as_posix() for run in runs]
        assert len(Path(expected_paths[-1]).parts) - 2 == 6
        for expected in reversed(expected_paths):
            assert require_active_run_path(hactors_root) == expected
            assert require_run_directory(hactors_root, project.name, expected) == project / expected
            parent = Path(expected).parent.as_posix()
            parent = "" if parent == "hactors" else parent
            assert select_parent_run(hactors_root) == parent
            assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": parent}
        assert snapshot(project) == before

    def test_switch_workflow_and_project_then_return(self, hactors_root, selected_chain):
        project, runs = selected_chain
        first = runs[-1].relative_to(project).as_posix()
        second = create_workflow(hactors_root, project.name).relative_to(project).as_posix()
        other = create_project("other", hactors_root)
        other_run = create_workflow(hactors_root, other.name).relative_to(other).as_posix()
        before = snapshot(project), snapshot(other)
        for name, path in [(project.name, first), (project.name, second), (other.name, other_run)]:
            set_active_run(hactors_root, name, path)
            assert load_state(hactors_root) == {"active_project": name, "active_run_path": path}
        set_active_project(hactors_root, project.name)
        assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": ""}
        set_active_run(hactors_root, project.name, first)
        assert require_active_run_path(hactors_root) == first
        set_active_run(hactors_root, other.name, "")
        assert load_state(hactors_root) == {"active_project": other.name, "active_run_path": ""}
        assert (snapshot(project), snapshot(other)) == before

    @pytest.mark.parametrize("old_state", [
        "active_project: old\ncurrent_workflow_run: ''\ncurrent_task_run: ''\ncurrent_rfc_run: ''\n",
        "active_project: [broken",
    ])
    def test_use_project_recovers_without_reading_old_state(self, hactors_root, selected_chain, old_state):
        project, runs = selected_chain
        before = snapshot(project)
        (hactors_root / "projects" / ".state.yaml").write_text(old_state)
        set_active_project(hactors_root, project.name)
        assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": ""}
        path = runs[-1].relative_to(project).as_posix()
        set_active_run(hactors_root, project.name, path)
        assert require_active_run_path(hactors_root) == path
        assert snapshot(project) == before


@pytest.mark.parametrize("problem", ["missing", "missing-manifest", "wrong-project", "malformed", "non-mapping"])
def test_project_validation_preserves_selection(hactors_root, selected_chain, problem, load_yaml):
    project, _ = selected_chain
    other = create_project("other", hactors_root)
    manifest = other / "manifest.yaml"
    name = other.name
    if problem == "missing":
        name = "nonexistent"
    elif problem == "missing-manifest":
        manifest.unlink()
    elif problem == "wrong-project":
        data = load_yaml(manifest)
        data["project"] = project.name
        manifest.write_text(yaml.safe_dump(data))
    else:
        manifest.write_text("project: [broken" if problem == "malformed" else "[]\n")
    before = snapshot(hactors_root / "projects")
    with pytest.raises(ValueError):
        require_project_directory(hactors_root, name)
    for select in (lambda: set_active_project(hactors_root, name),
                   lambda: set_active_run(hactors_root, name, "")):
        with pytest.raises(StateError):
            select()
    assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("name", ["", "../outside", "/tmp/outside", 42, None])
def test_invalid_project_names_rejected_without_mutation(hactors_root, selected_chain, name):
    before = snapshot(hactors_root / "projects")
    with pytest.raises(ValueError):
        require_project_directory(hactors_root, name)
    with pytest.raises(StateError):
        set_active_project(hactors_root, name)
    with pytest.raises(StateError):
        set_active_run(hactors_root, name, "")
    assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("case", [
    "absolute", "dot", "dotdot", "backslash", "double-slash", "trailing-slash",
    "file", "missing", "bare-id", "hactors-only", "empty", "wrong-prefix", "short-id",
    "unknown-suffix", "extra-manifest-suffix", "number", "none",
])
def test_entire_run_path_is_validated_without_normalizing(hactors_root, selected_chain, case):
    project, runs = selected_chain
    valid = runs[-1].relative_to(project).as_posix()
    paths = {
        "absolute": str(runs[-1]),
        "dot": valid.replace("hactors/", "hactors/./", 1),
        "dotdot": valid.replace("hactors/", "hactors/../hactors/", 1),
        "backslash": valid.replace("/", "\\"),
        "double-slash": valid.replace("/", "//", 1),
        "trailing-slash": valid + "/",
        "file": valid + "/manifest.yaml",
        "missing": valid + "/plan_run_999999",
        "bare-id": runs[0].name,
        "hactors-only": "hactors",
        "empty": "",
        "wrong-prefix": valid.replace("hactors/", "runs/", 1),
        "short-id": "hactors/workflow_run_1",
        "unknown-suffix": valid + "/unknown_000001",
        "extra-manifest-suffix": valid + "/manifest.yaml/plan_run_000001",
        "number": 42,
        "none": None,
    }
    before = snapshot(hactors_root / "projects")
    with pytest.raises(ValueError):
        require_run_directory(hactors_root, project.name, paths[case])
    # Empty is intentionally accepted by the setter as project-only selection.
    if case != "empty":
        with pytest.raises(StateError):
            set_active_run(hactors_root, project.name, paths[case])
    assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("parent_index,child_index", [(0, 2), (1, 3), (2, 4), (3, 1), (6, 0)])
def test_existing_directory_cannot_bypass_parent_child_rules(
    hactors_root, selected_chain, parent_index, child_index,
):
    project, runs = selected_chain
    parent, source = runs[parent_index], runs[child_index]
    wrong = parent / source.name
    wrong.mkdir()
    (wrong / "manifest.yaml").write_bytes((source / "manifest.yaml").read_bytes())
    before = snapshot(hactors_root / "projects")
    path = wrong.relative_to(project).as_posix()
    with pytest.raises(ValueError):
        require_run_directory(hactors_root, project.name, path)
    with pytest.raises(StateError):
        set_active_run(hactors_root, project.name, path)
    assert snapshot(hactors_root / "projects") == before


def test_repeated_instance_id_rejected_but_not_repeated_type(hactors_root, selected_chain):
    project, runs = selected_chain
    assert require_run_directory(hactors_root, project.name, runs[-1].relative_to(project).as_posix()) == runs[-1]
    duplicate = runs[3] / runs[2].name
    duplicate.mkdir()
    (duplicate / "manifest.yaml").write_bytes((runs[2] / "manifest.yaml").read_bytes())
    before = snapshot(hactors_root / "projects")
    path = duplicate.relative_to(project).as_posix()
    with pytest.raises(ValueError):
        require_run_directory(hactors_root, project.name, path)
    with pytest.raises(StateError):
        set_active_run(hactors_root, project.name, path)
    assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("index,problem", [
    (0, "wrong-wrapper"), (0, "wrong-id"), (1, "wrong-id"), (2, "wrong-id"),
    (3, "wrong-id"), (6, "wrong-id"), (0, "missing"), (3, "missing"), (6, "missing"),
    (0, "malformed"), (3, "non-mapping"), (6, "non-mapping-identity"),
])
def test_every_ancestor_manifest_is_validated(hactors_root, selected_chain, load_yaml, index, problem):
    project, runs = selected_chain
    manifest = runs[index] / "manifest.yaml"
    if problem == "missing":
        manifest.unlink()
    elif problem == "malformed":
        manifest.write_text("identity: [broken")
    elif problem == "non-mapping":
        manifest.write_text("[]\n")
    else:
        data = load_yaml(manifest)
        if problem == "wrong-wrapper":
            data = {"workflow_run_999999": data[runs[index].name]}
        else:
            body = data[runs[index].name] if index == 0 else data
            if problem == "non-mapping-identity":
                body["identity"] = []
            else:
                body["identity"]["id"] = "wrong_999999"
        manifest.write_text(yaml.safe_dump(data))
    path = runs[-1].relative_to(project).as_posix()
    before = snapshot(hactors_root / "projects")
    with pytest.raises(ValueError):
        require_run_directory(hactors_root, project.name, path)
    with pytest.raises(StateError):
        set_active_run(hactors_root, project.name, path)
    with pytest.raises(StateError):
        require_active_run_path(hactors_root)
    with pytest.raises(StateError):
        select_parent_run(hactors_root)
    assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("location", [
    "hactors", "workflow", "ancestor", "leaf", "ancestor-manifest", "leaf-manifest",
])
@pytest.mark.parametrize("external", [False, True], ids=["internal", "external"])
def test_symlinks_are_not_run_aliases(hactors_root, selected_chain, tmp_path, location, external):
    project, runs = selected_chain
    link = {
        "hactors": project / "hactors",
        "workflow": runs[0],
        "ancestor": runs[3],
        "leaf": runs[-1],
        "ancestor-manifest": runs[1] / "manifest.yaml",
        "leaf-manifest": runs[-1] / "manifest.yaml",
    }[location]
    destination = (tmp_path if external else project) / "original-node"
    is_directory = link.is_dir()
    link.rename(destination)
    link.symlink_to(destination, target_is_directory=is_directory)
    path = runs[-1].relative_to(project).as_posix()
    before = snapshot(hactors_root / "projects")
    target_before = snapshot(destination) if is_directory else destination.read_bytes()
    with pytest.raises(ValueError):
        require_run_directory(hactors_root, project.name, path)
    with pytest.raises(StateError):
        set_active_run(hactors_root, project.name, path)
    assert snapshot(hactors_root / "projects") == before
    assert (snapshot(destination) if is_directory else destination.read_bytes()) == target_before


@pytest.mark.parametrize("external", [False, True], ids=["internal", "external"])
def test_project_manifest_link_must_remain_inside_project(hactors_root, selected_chain, tmp_path, external):
    project, runs = selected_chain
    manifest = project / "manifest.yaml"
    target = (tmp_path if external else project) / "original-manifest.yaml"
    manifest.rename(target)
    manifest.symlink_to(target)
    before = snapshot(hactors_root / "projects"), target.read_bytes()
    path = runs[-1].relative_to(project).as_posix()
    if external:
        with pytest.raises(ValueError, match="fuera"):
            require_run_directory(hactors_root, project.name, path)
        with pytest.raises(StateError):
            set_active_run(hactors_root, project.name, path)
    else:
        assert require_run_directory(hactors_root, project.name, path) == runs[-1]
        assert require_active_run_path(hactors_root) == path
    assert (snapshot(hactors_root / "projects"), target.read_bytes()) == before
