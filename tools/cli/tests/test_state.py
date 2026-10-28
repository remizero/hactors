from pathlib import Path

import pytest
import yaml

from hactors_cli.core.state import (
    NoActiveProjectError,
    NoActiveWorkflowRunError,
    load_state,
    require_active_project,
    require_active_workflow_run,
    save_state,
    set_active_project,
    set_current_workflow_run,
)


class TestLoadState:
    def test_returns_defaults_when_no_file(self, hactors_root: Path):
        state = load_state(hactors_root)
        assert state == {"active_project": "", "current_workflow_run": ""}

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
