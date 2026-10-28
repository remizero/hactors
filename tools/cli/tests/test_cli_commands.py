from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.project import create_project
from hactors_cli.core.state import set_active_project


class TestUseProjectCli:
    def test_sets_active_project(self, hactors_root: Path, load_yaml):
        create_project("test-proj", hactors_root)

        runner = CliRunner()
        result = runner.invoke(cli, ["use-project", "test-proj", "--root", str(hactors_root)])

        assert result.exit_code == 0
        assert "Proyecto activo: test-proj" in result.output

        state = load_yaml(hactors_root / "projects" / ".state.yaml")
        assert state["active_project"] == "test-proj"

    def test_error_for_nonexistent_project(self, hactors_root: Path):
        runner = CliRunner()
        result = runner.invoke(cli, ["use-project", "nonexistent", "--root", str(hactors_root)])

        assert result.exit_code != 0
        assert "no encontrado" in result.output


class TestCreateWorkflowCli:
    def test_creates_workflow(self, hactors_root: Path):
        create_project("test-proj", hactors_root)

        runner = CliRunner()
        runner.invoke(cli, ["use-project", "test-proj", "--root", str(hactors_root)])
        result = runner.invoke(cli, [
            "create-workflow", "--task-ref", "task_001", "--root", str(hactors_root),
        ])

        assert result.exit_code == 0
        assert "Workflow creado" in result.output
        assert (hactors_root / "projects" / "test-proj" / "hactors" / "workflow_run_000001").is_dir()

    def test_error_without_active_project(self, hactors_root: Path):
        runner = CliRunner()
        result = runner.invoke(cli, ["create-workflow", "--root", str(hactors_root)])

        assert result.exit_code != 0
        assert "No hay proyecto activo" in result.output


class TestCreateTaskRunCli:
    def test_creates_task_run(self, hactors_root: Path):
        create_project("test-proj", hactors_root)

        runner = CliRunner()
        runner.invoke(cli, ["use-project", "test-proj", "--root", str(hactors_root)])
        runner.invoke(cli, ["create-workflow", "--root", str(hactors_root)])
        result = runner.invoke(cli, [
            "create-task-run", "--rfc-ref", "RFC-001", "--root", str(hactors_root),
        ])

        assert result.exit_code == 0
        assert "Task run creado" in result.output

        wf_dir = hactors_root / "projects" / "test-proj" / "hactors" / "workflow_run_000001"
        assert (wf_dir / "task_run_000001").is_dir()

    def test_error_without_active_workflow(self, hactors_root: Path):
        create_project("test-proj", hactors_root)

        runner = CliRunner()
        runner.invoke(cli, ["use-project", "test-proj", "--root", str(hactors_root)])
        result = runner.invoke(cli, ["create-task-run", "--root", str(hactors_root)])

        assert result.exit_code != 0
        assert "No hay workflow_run activo" in result.output
