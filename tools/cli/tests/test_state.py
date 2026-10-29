from pathlib import Path

import pytest
import yaml

from hactors_cli.core.state import (
    NoActiveProjectError,
    NoActiveRfcRunError,
    NoActiveTaskRunError,
    NoActiveWorkflowRunError,
    load_state,
    require_active_project,
    require_active_rfc_run,
    require_active_task_run,
    require_active_workflow_run,
    save_state,
    set_active_project,
    set_current_rfc_run,
    set_current_task_run,
    set_current_workflow_run,
)


class TestLoadState:
    def test_returns_defaults_when_no_file(self, hactors_root: Path):
        state = load_state(hactors_root)
        assert state == {
            "active_project": "", "current_workflow_run": "",
            "current_task_run": "", "current_rfc_run": "",
        }

    def test_returns_saved_state(self, hactors_root: Path):
        save_state(hactors_root, {"active_project": "test", "current_workflow_run": "wf_1"})
        state = load_state(hactors_root)
        assert state["active_project"] == "test"
        assert state["current_workflow_run"] == "wf_1"


class TestSetActiveProject:
    def test_sets_project_and_clears_workflow(self, hactors_root: Path):
        save_state(hactors_root, {"active_project": "old", "current_workflow_run": "wf_1"})
        set_active_project(hactors_root, "new-project")

        state = load_state(hactors_root)
        assert state["active_project"] == "new-project"
        assert state["current_workflow_run"] == ""

    def test_creates_state_file_if_missing(self, hactors_root: Path):
        set_active_project(hactors_root, "my-project")
        assert (hactors_root / "projects" / ".state.yaml").is_file()


class TestSetCurrentWorkflowRun:
    def test_sets_workflow_run(self, hactors_root: Path):
        set_active_project(hactors_root, "proj")
        set_current_workflow_run(hactors_root, "workflow_run_000001")

        state = load_state(hactors_root)
        assert state["current_workflow_run"] == "workflow_run_000001"


class TestRequireActiveProject:
    def test_raises_when_no_active(self, hactors_root: Path):
        with pytest.raises(NoActiveProjectError, match="No hay proyecto activo"):
            require_active_project(hactors_root)

    def test_returns_name_when_set(self, hactors_root: Path):
        set_active_project(hactors_root, "my-proj")
        assert require_active_project(hactors_root) == "my-proj"


class TestRequireActiveWorkflowRun:
    def test_raises_when_no_active(self, hactors_root: Path):
        set_active_project(hactors_root, "proj")
        with pytest.raises(NoActiveWorkflowRunError, match="No hay workflow_run activo"):
            require_active_workflow_run(hactors_root)

    def test_returns_id_when_set(self, hactors_root: Path):
        set_active_project(hactors_root, "proj")
        set_current_workflow_run(hactors_root, "workflow_run_000001")
        assert require_active_workflow_run(hactors_root) == "workflow_run_000001"


@pytest.mark.parametrize("reset", ["project", "workflow", "task"])
def test_changing_parent_clears_descendants(hactors_root, reset):
    set_active_project(hactors_root, "proj")
    set_current_workflow_run(hactors_root, "workflow_run_000001")
    set_current_task_run(hactors_root, "task_run_000001")
    set_current_rfc_run(hactors_root, "rfc_run_000001")
    if reset == "project":
        set_active_project(hactors_root, "other")
    elif reset == "workflow":
        set_current_workflow_run(hactors_root, "workflow_run_000002")
    else:
        set_current_task_run(hactors_root, "task_run_000002")
    state = load_state(hactors_root)
    assert state["current_rfc_run"] == ""
    assert state["current_task_run"] == ("task_run_000002" if reset == "task" else "")
    assert state["current_workflow_run"] == {
        "project": "", "workflow": "workflow_run_000002", "task": "workflow_run_000001",
    }[reset]
    assert state["active_project"] == ("other" if reset == "project" else "proj")


@pytest.mark.parametrize("require,error", [
    (require_active_task_run, NoActiveTaskRunError),
    (require_active_rfc_run, NoActiveRfcRunError),
])
def test_require_missing_descendant(hactors_root, require, error):
    with pytest.raises(error, match="No hay"):
        require(hactors_root)


def test_descendant_state_is_preserved(hactors_root):
    set_active_project(hactors_root, "proj")
    set_current_workflow_run(hactors_root, "workflow_run_000001")
    set_current_task_run(hactors_root, "task_run_000001")
    set_current_rfc_run(hactors_root, "rfc_run_000001")
    assert require_active_task_run(hactors_root) == "task_run_000001"
    assert require_active_rfc_run(hactors_root) == "rfc_run_000001"
    assert require_active_workflow_run(hactors_root) == "workflow_run_000001"
    assert require_active_project(hactors_root) == "proj"


def test_absent_descendant_fields_are_empty(hactors_root):
    save_state(hactors_root, {"active_project": "proj", "current_workflow_run": "workflow_run_000001"})
    state = load_state(hactors_root)
    assert state["current_task_run"] == state["current_rfc_run"] == ""
