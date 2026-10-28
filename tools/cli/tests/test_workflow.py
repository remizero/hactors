from pathlib import Path

import pytest
import yaml

from hactors_cli.core.project import create_project
from hactors_cli.core.state import set_active_project
from hactors_cli.core.task_run import TaskRunError, create_task_run
from hactors_cli.core.workflow import WorkflowError, create_workflow


class TestCreateWorkflow:
    def test_creates_workflow_run_directory(self, hactors_root: Path):
        create_project("test-proj", hactors_root)

        run_dir = create_workflow(hactors_root, "test-proj", task_ref="task_000001")

        assert run_dir.is_dir()
        assert run_dir.name == "workflow_run_000001"
        assert (run_dir / "manifest.yaml").is_file()

    def test_increments_counter_in_manifest(self, hactors_root: Path, load_yaml):
        create_project("test-proj", hactors_root)

        create_workflow(hactors_root, "test-proj")

        manifest = load_yaml(hactors_root / "projects" / "test-proj" / "manifest.yaml")
        assert manifest["counters"]["workflow_run"] == 1

    def test_sequential_workflow_runs(self, hactors_root: Path):
        create_project("test-proj", hactors_root)

        run1 = create_workflow(hactors_root, "test-proj")
        run2 = create_workflow(hactors_root, "test-proj")

        assert run1.name == "workflow_run_000001"
        assert run2.name == "workflow_run_000002"

    def test_manifest_has_task_ref(self, hactors_root: Path, load_yaml):
        create_project("test-proj", hactors_root)

        run_dir = create_workflow(hactors_root, "test-proj", task_ref="task_000001")

        manifest = load_yaml(run_dir / "manifest.yaml")
        run_data = manifest["workflow_run_000001"]
        assert run_data["identity"]["id"] == "workflow_run_000001"
        assert run_data["identity"]["task_ref"] == "task_000001"

    def test_updates_state(self, hactors_root: Path, load_yaml):
        create_project("test-proj", hactors_root)

        create_workflow(hactors_root, "test-proj")

        state = load_yaml(hactors_root / "projects" / ".state.yaml")
        assert state["current_workflow_run"] == "workflow_run_000001"

    def test_error_for_nonexistent_project(self, hactors_root: Path):
        with pytest.raises(WorkflowError, match="no encontrado"):
            create_workflow(hactors_root, "nonexistent")

    def test_yaml_fields_from_template(self, hactors_root: Path, load_yaml):
        create_project("test-proj", hactors_root)

        template_path = hactors_root / "specs" / "templates" / "workflow_run_manifest_template.yaml"
        with template_path.open() as f:
            template = yaml.safe_load(f)

        run_dir = create_workflow(hactors_root, "test-proj")
        manifest = load_yaml(run_dir / "manifest.yaml")
        run_data = manifest["workflow_run_000001"]

        for key in template:
            assert key in run_data, f"Campo '{key}' de la plantilla falta en manifest generado"


class TestCreateTaskRun:
    def test_creates_task_run_inside_workflow(self, hactors_root: Path):
        create_project("test-proj", hactors_root)

        wf = create_workflow(hactors_root, "test-proj")
        tr = create_task_run(hactors_root, "test-proj", wf.name, rfc_ref="RFC-001")

        assert tr.is_dir()
        assert tr.name == "task_run_000001"
        assert tr.parent == wf
        assert (tr / "manifest.yaml").is_file()

    def test_increments_counter_in_manifest(self, hactors_root: Path, load_yaml):
        create_project("test-proj", hactors_root)

        wf = create_workflow(hactors_root, "test-proj")
        create_task_run(hactors_root, "test-proj", wf.name)

        manifest = load_yaml(hactors_root / "projects" / "test-proj" / "manifest.yaml")
        assert manifest["counters"]["task_run"] == 1

    def test_sequential_task_runs(self, hactors_root: Path):
        create_project("test-proj", hactors_root)

        wf = create_workflow(hactors_root, "test-proj")
        tr1 = create_task_run(hactors_root, "test-proj", wf.name)
        tr2 = create_task_run(hactors_root, "test-proj", wf.name)

        assert tr1.name == "task_run_000001"
        assert tr2.name == "task_run_000002"

    def test_manifest_has_rfc_ref(self, hactors_root: Path, load_yaml):
        create_project("test-proj", hactors_root)

        wf = create_workflow(hactors_root, "test-proj")
        tr = create_task_run(hactors_root, "test-proj", wf.name, rfc_ref="RFC-001")

        manifest = load_yaml(tr / "manifest.yaml")
        assert manifest["identity"]["id"] == "task_run_000001"
        assert manifest["identity"]["rfc_ref"] == "RFC-001"

    def test_error_for_nonexistent_project(self, hactors_root: Path):
        with pytest.raises(TaskRunError, match="no encontrado"):
            create_task_run(hactors_root, "nonexistent", "workflow_run_000001")

    def test_error_for_nonexistent_workflow(self, hactors_root: Path):
        create_project("test-proj", hactors_root)

        with pytest.raises(TaskRunError, match="Workflow run no encontrado"):
            create_task_run(hactors_root, "test-proj", "workflow_run_999999")

    def test_yaml_fields_from_template(self, hactors_root: Path, load_yaml):
        create_project("test-proj", hactors_root)

        template_path = hactors_root / "specs" / "templates" / "task_run_template.yaml"
        with template_path.open() as f:
            template = yaml.safe_load(f)

        wf = create_workflow(hactors_root, "test-proj")
        tr = create_task_run(hactors_root, "test-proj", wf.name)
        manifest = load_yaml(tr / "manifest.yaml")

        for key in template:
            assert key in manifest, f"Campo '{key}' de la plantilla falta en manifest generado"
