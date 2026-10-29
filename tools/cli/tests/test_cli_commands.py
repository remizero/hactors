import os
import subprocess
import sys
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
            "create-task-run", "--root", str(hactors_root),
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


@pytest.mark.parametrize("command,steps,missing", [
    ("create-rfc-run", 0, "proyecto"),
    ("create-rfc-run", 1, "workflow_run"),
    ("create-rfc-run", 2, "task_run"),
    ("create-plan-run", 0, "proyecto"),
    ("create-plan-run", 1, "workflow_run"),
    ("create-plan-run", 2, "task_run"),
    ("create-plan-run", 3, "rfc_run"),
])
def test_new_commands_require_parent_context(hactors_root, command, steps, missing):
    create_project("proj", hactors_root)
    runner = CliRunner()
    setup = [["use-project", "proj"], ["create-workflow"], ["create-task-run"]]
    for args in setup[:steps]:
        result = runner.invoke(cli, [*args, "--root", str(hactors_root)])
        assert result.exit_code == 0, result.output
    result = runner.invoke(cli, [command, "--root", str(hactors_root)])
    assert result.exit_code == 1
    assert f"No hay {missing} activo" in result.output


@pytest.mark.parametrize("command", ["create-rfc-run", "create-plan-run"])
def test_new_command_help(command):
    result = CliRunner().invoke(cli, [command, "--help"])
    assert result.exit_code == 0
    assert ("--rfc-ref" if command == "create-rfc-run" else "--plan-ref") in result.output


def test_task_run_no_longer_accepts_rfc_ref():
    result = CliRunner().invoke(cli, ["create-task-run", "--rfc-ref", "RFC-A00001"])
    assert result.exit_code == 2
    assert "No such option" in result.output
    assert "--rfc-ref" in result.output


def test_cli_process_chain(hactors_root, load_yaml):
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))

    def invoke(*args, expected=0):
        result = subprocess.run(
            [sys.executable, "-m", "hactors_cli", *args, "--root", str(hactors_root)],
            cwd=hactors_root, env=env, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == expected, result.stdout + result.stderr
        return result

    invoke("create-project", "proj")
    project = hactors_root / "projects" / "proj"
    rfc_doc = project / "rfcs" / "RFC-A00001.md"
    plan_doc = project / "rfcs" / "plans" / "PLAN-00001.md"
    plan_doc.parent.mkdir()
    rfc_doc.write_text("RFC original\n")
    plan_doc.write_text("PLAN original\n")
    originals = {path: path.read_bytes() for path in (rfc_doc, plan_doc)}
    invoke("use-project", "proj")
    invoke("create-workflow", "--task-ref", "task_000001")
    invoke("create-task-run")
    invoke("create-rfc-run", "--rfc-ref", "RFC-A00001")
    invoke("create-plan-run", "--plan-ref", "PLAN-00001")
    workflow = project / "hactors" / "workflow_run_000001"
    task = workflow / "task_run_000001"
    rfc = task / "rfc_run_000001"
    plan = rfc / "plan_run_000001"
    assert load_yaml(rfc / "manifest.yaml")["identity"]["rfc_ref"] == "RFC-A00001"
    assert load_yaml(plan / "manifest.yaml")["identity"]["plan_ref"] == "PLAN-00001"
    assert load_yaml(task / "manifest.yaml")["identity"] == {"id": "task_run_000001"}
    assert load_yaml(project / "manifest.yaml")["counters"] == {
        "task": 0, "workflow_run": 1, "task_run": 1, "rfc_run": 1, "plan_run": 1,
    }
    assert load_yaml(hactors_root / "projects" / ".state.yaml") == {
        "active_project": "proj", "current_workflow_run": workflow.name,
        "current_task_run": task.name, "current_rfc_run": rfc.name,
    }
    invoke("create-plan-run", "--plan-ref", "PLAN-00002")
    assert (rfc / "plan_run_000002" / "manifest.yaml").is_file()
    invoke("create-task-run")
    result = invoke("create-plan-run", expected=1)
    assert "No hay rfc_run activo" in result.stderr
    invoke("create-rfc-run", "--rfc-ref", "RFC-F00001")
    assert (workflow / "task_run_000002" / "rfc_run_000002" / "manifest.yaml").is_file()
    invoke("create-workflow")
    result = invoke("create-rfc-run", expected=1)
    assert "No hay task_run activo" in result.stderr
    invoke("create-project", "other")
    invoke("use-project", "other")
    result = invoke("create-plan-run", expected=1)
    assert "No hay workflow_run activo" in result.stderr
    assert all(path.read_bytes() == content for path, content in originals.items())
