import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.project import create_project
from hactors_cli.core.state import load_state


def snapshot(directory):
    return {
        path.relative_to(directory).as_posix(): (
            ("link", str(path.readlink())) if path.is_symlink() else
            ("directory",) if path.is_dir() else ("file", path.read_bytes())
        )
        for path in directory.rglob("*")
    }


def invoke(root, *args, expected=0):
    result = CliRunner().invoke(cli, [*args, "--root", str(root)])
    assert result.exit_code == expected, result.output
    assert "Traceback" not in result.output
    return result


@pytest.fixture(params=["rfc_run", "test_run", "harness_run"])
def cli_chain(hactors_root, request):
    project = create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", project.name)
    paths = []
    for command in (
        "create-workflow", "create-task-run", "create-rfc-run", "create-plan-run",
        "create-rfc-run", "create-plan-run", "create-rfc-run",
    ):
        invoke(hactors_root, command)
        paths.append(load_state(hactors_root)["active_run_path"])
    if request.param in ("test_run", "harness_run"):
        invoke(hactors_root, "create-test-run")
        paths.append(load_state(hactors_root)["active_run_path"])
    if request.param == "harness_run":
        invoke(hactors_root, "create-harness-run")
        paths.append(load_state(hactors_root)["active_run_path"])
    return project, paths


def test_use_project_sets_exact_state_and_clears_run(hactors_root, cli_chain, load_yaml):
    project, _ = cli_chain
    result = invoke(hactors_root, "use-project", project.name)
    assert "Proyecto activo: proj" in result.output
    assert load_yaml(hactors_root / "projects" / ".state.yaml") == {
        "active_project": project.name, "active_run_path": "",
    }


def test_use_project_requires_existing_project(hactors_root):
    before = snapshot(hactors_root / "projects")
    result = invoke(hactors_root, "use-project", "nonexistent", expected=1)
    assert "no encontrado" in result.output
    assert snapshot(hactors_root / "projects") == before


def test_creates_workflow_and_task_with_reference(hactors_root, load_yaml):
    project = create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", project.name)
    workflow_result = invoke(hactors_root, "create-workflow", "--task-ref", "TASK-00001")
    assert "Workflow creado" in workflow_result.output
    task_result = invoke(hactors_root, "create-task-run")
    assert "Task run creado" in task_result.output
    workflow = project / "hactors" / "workflow_run_000001"
    task = workflow / "task_run_000001"
    assert load_yaml(workflow / "manifest.yaml")[workflow.name]["identity"]["task_ref"] == "TASK-00001"
    assert load_yaml(task / "manifest.yaml")["identity"] == {"id": task.name}
    assert load_state(hactors_root) == {
        "active_project": project.name, "active_run_path": task.relative_to(project).as_posix(),
    }


@pytest.mark.parametrize("command,steps,message", [
    ("create-workflow", 0, "No hay proyecto activo"),
    ("create-task-run", 0, "No hay proyecto activo"),
    ("create-rfc-run", 0, "No hay proyecto activo"),
    ("create-plan-run", 0, "No hay proyecto activo"),
    ("create-task-run", 1, "No hay instancia activa"),
    ("create-rfc-run", 1, "No hay instancia activa"),
    ("create-plan-run", 1, "No hay instancia activa"),
    ("create-rfc-run", 2, "No se puede crear"),
    ("create-plan-run", 2, "No se puede crear"),
    ("create-plan-run", 3, "No se puede crear"),
    ("create-task-run", 3, "No se puede crear"),
    ("create-rfc-run", 4, "No se puede crear"),
    ("create-task-run", 5, "No se puede crear"),
    ("create-plan-run", 5, "No se puede crear"),
    ("create-test-run", 0, "No hay proyecto activo"),
    ("create-test-run", 1, "No hay instancia activa"),
    ("create-test-run", 2, "No se puede crear"),
    ("create-test-run", 3, "No se puede crear"),
    ("create-test-run", 5, "No se puede crear"),
    ("create-harness-run", 0, "No hay proyecto activo"),
    ("create-harness-run", 1, "No hay instancia activa"),
    ("create-harness-run", 2, "No se puede crear"),
    ("create-harness-run", 3, "No se puede crear"),
    ("create-harness-run", 4, "No se puede crear"),
    ("create-harness-run", 5, "No se puede crear"),
])
def test_commands_require_selected_leaf_without_falling_back(hactors_root, command, steps, message):
    create_project("proj", hactors_root)
    setup = [
        ("use-project", "proj"), ("create-workflow",), ("create-task-run",),
        ("create-rfc-run",), ("create-plan-run",),
    ]
    for args in setup[:steps]:
        invoke(hactors_root, *args)
    before = snapshot(hactors_root / "projects")
    result = invoke(hactors_root, command, expected=1)
    assert message in result.output
    if steps >= 2:
        assert "dentro de" in result.output
    assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("command,option", [
    ("create-rfc-run", "--rfc-ref"), ("create-plan-run", "--plan-ref"),
    ("create-test-run", "--test-ref"), ("use-run", "--parent"),
    ("create-harness-run", "--harness-ref"), ("create-harness-run", "--content-ref"),
])
def test_new_command_help(command, option):
    result = CliRunner().invoke(cli, [command, "--help"])
    assert result.exit_code == 0
    assert option in result.output
    assert "--root" in result.output


def test_task_run_no_longer_accepts_rfc_ref():
    result = CliRunner().invoke(cli, ["create-task-run", "--rfc-ref", "RFC-A00001"])
    assert result.exit_code == 2
    assert "No such option" in result.output
    assert "--rfc-ref" in result.output


@pytest.mark.parametrize("both", [False, True], ids=["neither", "both"])
def test_use_run_requires_exactly_one_selector(hactors_root, cli_chain, both):
    _, paths = cli_chain
    args = [paths[-1], "--parent"] if both else []
    before = snapshot(hactors_root / "projects")
    invoke(hactors_root, "use-run", *args, expected=2)
    assert snapshot(hactors_root / "projects") == before


def test_use_run_requires_project_and_parent_requires_run(hactors_root):
    before = snapshot(hactors_root / "projects")
    result = invoke(hactors_root, "use-run", "hactors/workflow_run_000001", expected=1)
    assert "No hay proyecto activo" in result.output
    assert snapshot(hactors_root / "projects") == before
    create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", "proj")
    before = snapshot(hactors_root / "projects")
    result = invoke(hactors_root, "use-run", "--parent", expected=1)
    assert "No hay instancia activa" in result.output
    assert snapshot(hactors_root / "projects") == before


def test_use_run_parent_visits_every_ancestor_then_project(hactors_root, cli_chain):
    project, paths = cli_chain
    before = snapshot(project)
    for path in reversed(paths[:-1]):
        invoke(hactors_root, "use-run", "--parent")
        assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": path}
    invoke(hactors_root, "use-run", "--parent")
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": ""}
    invoke(hactors_root, "use-run", "--parent", expected=1)
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": ""}
    assert snapshot(project) == before


@pytest.mark.parametrize("command", ["use-run", "create-harness-run"])
@pytest.mark.parametrize("case", ["absolute", "bare-id", "dotdot", "trailing", "file", "suffix", "missing"])
def test_selection_and_creation_reject_invalid_full_path_without_mutation(hactors_root, cli_chain, command, case):
    project, paths = cli_chain
    path = {
        "absolute": str(project / paths[-1]), "bare-id": "workflow_run_000001",
        "dotdot": paths[0] + "/../workflow_run_000001", "trailing": paths[-1] + "/",
        "file": paths[-1] + "/manifest.yaml", "suffix": paths[-1] + "/unknown_000001",
        "missing": str(Path(paths[-1]).with_name(Path(paths[-1]).name.rsplit("_", 1)[0] + "_999999")),
    }[case]
    if command == "create-harness-run":
        (hactors_root / "projects" / ".state.yaml").write_text(yaml.safe_dump({
            "active_project": project.name, "active_run_path": path,
        }))
    before = snapshot(hactors_root / "projects")
    args = [path] if command == "use-run" else []
    result = invoke(hactors_root, command, *args, expected=1)
    assert any(word in result.output.lower() for word in ("ruta", "parent", "padre", "manifest"))
    assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("command,content", [
    ("create-workflow", "active_project: [broken"),
    ("create-workflow", b"\xff"),
    ("create-task-run", "[]\n"),
    ("create-rfc-run", "active_project: false\n"),
    ("create-plan-run", "active_project: proj\nactive_run_path: []\n"),
    ("create-test-run", "active_project: proj\nactive_run_path: []\n"),
    ("create-test-run", "active_project: [broken"),
    ("create-harness-run", "active_project: proj\nactive_run_path: []\n"),
    ("create-harness-run", "active_project: [broken"),
    ("create-harness-run", "[]\n"),
    ("create-harness-run", "active_project: false\n"),
    ("create-harness-run", b"\xff"),
    ("use-run", "active_project: proj\nactive_run_path: 42\n"),
    ("use-run", "active_project: ''\nactive_run_path: hactors/workflow_run_000001\n"),
])
def test_corrupt_state_reports_error_without_traceback_or_mutation(hactors_root, command, content):
    project = create_project("proj", hactors_root)
    state_file = hactors_root / "projects" / ".state.yaml"
    state_file.write_bytes(content if isinstance(content, bytes) else content.encode())
    before = snapshot(hactors_root / "projects")
    args = ["--parent"] if command == "use-run" else []
    result = invoke(hactors_root, command, *args, expected=1)
    assert "error" in result.output.lower()
    assert snapshot(hactors_root / "projects") == before
    invoke(hactors_root, "use-project", project.name)
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": ""}


@pytest.mark.parametrize("problem", ["wrong-project", "wrong-wrapper", "wrong-ancestor-id", "malformed-manifest"])
def test_invalid_manifest_is_reported_by_selection_and_creation(hactors_root, cli_chain, load_yaml, problem):
    project, paths = cli_chain
    if problem == "wrong-project":
        manifest = project / "manifest.yaml"
        data = load_yaml(manifest)
        data["project"] = "other"
    elif problem == "wrong-wrapper":
        manifest = project / paths[0] / "manifest.yaml"
        data = {"workflow_run_999999": load_yaml(manifest)["workflow_run_000001"]}
    else:
        manifest = project / paths[3] / "manifest.yaml"
        data = load_yaml(manifest)
        data["identity"]["id"] = "plan_run_999999"
    manifest.write_text("identity: [broken" if problem == "malformed-manifest" else yaml.safe_dump(data))
    before = snapshot(hactors_root / "projects")
    for args in (
        ("use-run", paths[-1]), ("use-run", "--parent"), ("create-plan-run",),
        ("create-test-run",), ("create-harness-run",),
    ):
        result = invoke(hactors_root, *args, expected=1)
        assert "manifest" in result.output.lower()
        assert snapshot(hactors_root / "projects") == before


@pytest.mark.parametrize("cli_chain", ["rfc_run"], indirect=True)
@pytest.mark.parametrize("prefix,field", [
    ("test_run", "test_ref"), ("harness_run", "harness_ref"), ("harness_run", "content_ref"),
])
@pytest.mark.parametrize("parent_index", [2, 6], ids=["initial-rfc", "deep-rfc"])
@pytest.mark.parametrize("reference", [None, "", "opaque test reference", "../missing", "línea: uno\n# literal"])
def test_create_run_uses_selected_parent_and_verbatim_reference(
    hactors_root, cli_chain, load_yaml, prefix, field, parent_index, reference,
):
    project, paths = cli_chain
    paths = list(paths)
    parent = paths[parent_index]
    invoke(hactors_root, "use-run", parent)
    if prefix == "harness_run":
        invoke(hactors_root, "create-test-run")
        parent = load_state(hactors_root)["active_run_path"]
        paths.append(parent)
    counters = load_yaml(project / "manifest.yaml")["counters"].copy()
    originals = {path: (project / path / "manifest.yaml").read_bytes() for path in paths}
    templates = snapshot(hactors_root / "specs" / "templates")
    args = [] if reference is None else ["--" + field.replace("_", "-"), reference]
    command = "create-" + prefix.replace("_", "-")
    result = invoke(hactors_root, command, *args)
    assert f"{prefix.split('_')[0].title()} run creado" in result.output
    path = f"{parent}/{prefix}_000001"
    run = project / path
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": path}
    expected = {
        "identity": {"id": run.name, field: "" if reference is None else reference},
        "state": {"status": "", "blocked_reason": ""},
    }
    if prefix == "harness_run":
        expected["identity"].setdefault("harness_ref", "")
        expected["identity"].setdefault("content_ref", "")
        expected["execution"] = {"source_revision": "", "parameters": {}}
    assert load_yaml(run / "manifest.yaml") == expected
    assert list(run.iterdir()) == [run / "manifest.yaml"]
    counters[prefix] += 1
    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    assert all((project / path / "manifest.yaml").read_bytes() == content for path, content in originals.items())
    assert snapshot(hactors_root / "specs" / "templates") == templates
    assert list((project / "rfcs").iterdir()) == []
    invoke(hactors_root, "use-run", "--parent")
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": parent}
    invoke(hactors_root, command)
    sibling = f"{parent}/{prefix}_000002"
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": sibling}
    before = snapshot(project)
    invoke(hactors_root, "use-run", path)
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": path}
    assert snapshot(project) == before


@pytest.mark.parametrize("cli_chain,prefix", [("rfc_run", "test_run"), ("test_run", "harness_run")], indirect=["cli_chain"])
def test_cli_legacy_project_uses_template_defaults_and_adds_only_own_counter(hactors_root, cli_chain, load_yaml, prefix):
    project, paths = cli_chain
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"].pop(prefix)
    manifest.write_text(yaml.safe_dump(data))
    source = hactors_root / "specs" / "templates" / f"{prefix}_template.yaml"
    template = load_yaml(source)
    template["state"].update(status="pending", blocked_reason="manual approval")
    if prefix == "harness_run":
        template["identity"].update(harness_ref="default HRN@v1", content_ref="default content")
        template["execution"].update(source_revision="default revision", parameters={"timeout": 12})
    source.write_text(yaml.safe_dump(template))
    originals = source.read_bytes(), (project / paths[-1] / "manifest.yaml").read_bytes()
    invoke(hactors_root, "create-" + prefix.replace("_", "-"))
    path = f"{paths[-1]}/{prefix}_000001"
    template["identity"]["id"] = f"{prefix}_000001"
    assert load_yaml(project / path / "manifest.yaml") == template
    data["counters"][prefix] = 1
    assert load_yaml(manifest) == data
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": path}
    assert (source.read_bytes(), (project / paths[-1] / "manifest.yaml").read_bytes()) == originals


@pytest.mark.parametrize("cli_chain,command", [
    (parent, command)
    for parent in ("test_run", "harness_run")
    for command in ("create-task-run", "create-rfc-run", "create-plan-run", "create-test-run", "create-harness-run")
    if not (parent == "test_run" and command == "create-harness-run")
], indirect=["cli_chain"])
def test_cli_test_and_harness_reject_incompatible_child_creators_without_mutation(hactors_root, cli_chain, command):
    _, paths = cli_chain
    prefix = Path(paths[-1]).name.rsplit("_", 1)[0]
    before = snapshot(hactors_root)
    result = invoke(hactors_root, command, expected=1)
    assert "No se puede crear" in result.output
    assert f"dentro de un {prefix}" in result.output
    assert "use-run" in result.output
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("cli_chain", ["test_run", "harness_run"], indirect=True)
def test_create_workflow_from_test_or_harness_still_creates_at_project_level(hactors_root, cli_chain, load_yaml):
    project, paths = cli_chain
    branch = project / paths[0]
    before = snapshot(branch)
    counters = load_yaml(project / "manifest.yaml")["counters"].copy()
    invoke(hactors_root, "create-workflow")
    assert load_state(hactors_root) == {
        "active_project": project.name, "active_run_path": "hactors/workflow_run_000002",
    }
    counters["workflow_run"] += 1
    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    assert snapshot(branch) == before


@pytest.mark.parametrize("cli_chain,prefix", [("rfc_run", "test_run"), ("test_run", "harness_run")], indirect=["cli_chain"])
@pytest.mark.parametrize("problem,message", [
    ("missing-template", "Plantilla no encontrada"),
    ("broken-template", "error"),
    ("counter", "Contador inválido"),
    ("counter-map", "Contadores inválidos"),
    ("collision", "Ya existe"),
])
def test_create_run_cli_errors_are_clear_and_do_not_write(hactors_root, cli_chain, load_yaml, prefix, problem, message):
    project, paths = cli_chain
    source = hactors_root / "specs" / "templates" / f"{prefix}_template.yaml"
    if problem == "missing-template":
        source.unlink()
    elif problem == "broken-template":
        source.write_text("identity: [broken")
    elif problem in ("counter", "counter-map"):
        manifest = project / "manifest.yaml"
        data = load_yaml(manifest)
        if problem == "counter":
            data["counters"][prefix] = True
        else:
            data["counters"] = []
        manifest.write_text(yaml.safe_dump(data))
    else:
        (project / paths[-1] / f"{prefix}_000001").write_text("never overwrite\n")
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-" + prefix.replace("_", "-"), expected=1)
    assert message.lower() in result.output.lower()
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("cli_chain", ["test_run", "harness_run"], indirect=True)
@pytest.mark.parametrize("problem", [
    "wrong-id", "missing-manifest", "leaf-symlink", "leaf-manifest-symlink",
    "ancestor-symlink", "ancestor-manifest-symlink",
])
def test_cli_selecting_test_or_harness_validates_identity_and_symlinks(hactors_root, cli_chain, load_yaml, tmp_path, problem):
    project, paths = cli_chain
    leaf = project / paths[-1]
    manifest = leaf / "manifest.yaml"
    if problem == "wrong-id":
        data = load_yaml(manifest)
        data["identity"]["id"] = leaf.name.rsplit("_", 1)[0] + "_999999"
        manifest.write_text(yaml.safe_dump(data))
    elif problem == "missing-manifest":
        manifest.unlink()
    else:
        node = project / paths[3] if problem.startswith("ancestor") else leaf
        if "manifest" in problem:
            node /= "manifest.yaml"
        is_directory = node.is_dir()
        target = tmp_path / "original-node"
        node.rename(target)
        node.symlink_to(target, target_is_directory=is_directory)
    before = snapshot(tmp_path)
    for args in (("use-run", paths[-1]), ("use-run", "--parent"), ("create-test-run",), ("create-harness-run",)):
        result = invoke(hactors_root, *args, expected=1)
        assert any(word in result.output.lower() for word in ("manifest", "enlace"))
        assert snapshot(tmp_path) == before


def test_top_level_help_lists_harness_command():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "create-harness-run" in result.output


@pytest.mark.parametrize("cli_chain", ["test_run"], indirect=True)
@pytest.mark.parametrize("explicit_root", [False, True], ids=["autodetect-deep-cwd", "explicit-root-outside-cwd"])
def test_harness_cli_root_resolution(hactors_root, cli_chain, monkeypatch, tmp_path, load_yaml, explicit_root):
    project, paths = cli_chain
    monkeypatch.chdir(tmp_path if explicit_root else project / paths[-1])
    args = ["create-harness-run", "--harness-ref", "HRN-00001@v1", "--content-ref", "content: # opaque"]
    if explicit_root:
        args += ["--root", str(hactors_root)]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0, result.output
    assert "Harness run creado" in result.output
    path = f"{paths[-1]}/harness_run_000001"
    assert load_state(hactors_root) == {"active_project": project.name, "active_run_path": path}
    assert load_yaml(project / path / "manifest.yaml")["identity"] == {
        "id": "harness_run_000001", "harness_ref": "HRN-00001@v1", "content_ref": "content: # opaque",
    }


@pytest.mark.parametrize("cli_chain", ["test_run"], indirect=True)
@pytest.mark.parametrize("fields", [(), ("harness_ref",), ("content_ref",), ("harness_ref", "content_ref")])
def test_harness_cli_empty_refs_override_only_supplied_template_defaults(hactors_root, cli_chain, load_yaml, fields):
    project, paths = cli_chain
    source = hactors_root / "specs" / "templates" / "harness_run_template.yaml"
    template = load_yaml(source)
    template["identity"].update(harness_ref="default HRN@v1", content_ref="default content")
    source.write_text(yaml.safe_dump(template))
    original = source.read_bytes()
    args = [arg for field in fields for arg in ("--" + field.replace("_", "-"), "")]
    invoke(hactors_root, "create-harness-run", *args)
    template["identity"].update(id="harness_run_000001", **{field: "" for field in fields})
    assert load_yaml(project / paths[-1] / "harness_run_000001" / "manifest.yaml") == template
    assert source.read_bytes() == original


@pytest.mark.parametrize("cli_chain", ["test_run"], indirect=True)
def test_harness_cli_rejects_non_mapping_template_identity_before_writes(hactors_root, cli_chain):
    source = hactors_root / "specs" / "templates" / "harness_run_template.yaml"
    source.write_text("identity: []\n")
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-harness-run", expected=1)
    assert "identity" in result.output
    assert snapshot(hactors_root) == before


def test_cli_process_chain(hactors_root, load_yaml):
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]), PYTHONDONTWRITEBYTECODE="1")

    def process(*args, expected=0):
        result = subprocess.run(
            [sys.executable, "-m", "hactors_cli", *args, "--root", str(hactors_root)],
            cwd=hactors_root, env=env, capture_output=True, text=True, timeout=30,
        )
        output = result.stdout + result.stderr
        assert result.returncode == expected, output
        assert "Traceback" not in output
        return output

    process("create-project", "proj")
    project = hactors_root / "projects" / "proj"
    state_file = hactors_root / "projects" / ".state.yaml"
    references = ["RFC-A00001", "RFC-A00001-F00001", "RFC-A00001-F00001-T00001", "RFC-A00001-F00002"]
    (project / "rfcs" / "plans").mkdir()
    documents = [project / "rfcs" / f"{ref}.md" for ref in references]
    documents += [project / "rfcs" / "plans" / f"PLAN-{index:05d}.md" for index in (1, 2)]
    documents.append(project / "tasks" / "TASK-00001.md")
    for path in documents:
        path.write_text(f"Original {path.stem}\n")
    originals = {path: path.read_bytes() for path in documents}
    source_templates = snapshot(hactors_root / "specs" / "templates")

    process("use-project", "proj")
    process("create-workflow", "--task-ref", "TASK-00001")
    process("create-task-run")
    process("create-rfc-run", "--rfc-ref", references[0])
    process("create-plan-run", "--plan-ref", "PLAN-00001")
    process("create-rfc-run", "--rfc-ref", references[1])
    process("create-plan-run", "--plan-ref", "PLAN-00002")
    process("create-rfc-run", "--rfc-ref", references[2])
    workflow = project / "hactors" / "workflow_run_000001"
    task = workflow / "task_run_000001"
    rfc1 = task / "rfc_run_000001"
    plan1 = rfc1 / "plan_run_000001"
    rfc2 = plan1 / "rfc_run_000002"
    plan2 = rfc2 / "plan_run_000002"
    rfc3 = plan2 / "rfc_run_000003"
    runs = [workflow, task, rfc1, plan1, rfc2, plan2, rfc3]
    for run, ref in zip((rfc1, rfc2, rfc3), references):
        assert load_yaml(run / "manifest.yaml")["identity"] == {"id": run.name, "rfc_ref": ref}
    for index, run in enumerate((plan1, plan2), 1):
        assert load_yaml(run / "manifest.yaml")["identity"] == {"id": run.name, "plan_ref": f"PLAN-{index:05d}"}
    assert load_yaml(workflow / "manifest.yaml")[workflow.name]["identity"]["task_ref"] == "TASK-00001"
    assert load_yaml(task / "manifest.yaml")["identity"] == {"id": task.name}
    originals.update({run / "manifest.yaml": (run / "manifest.yaml").read_bytes() for run in runs})
    deepest = rfc3.relative_to(project).as_posix()
    assert len(Path(deepest).parts) - 2 == 6
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": deepest}
    counters = {
        "task": 0, "workflow_run": 1, "task_run": 1, "rfc_run": 3, "plan_run": 2,
        "test_run": 0, "harness_run": 0, "evidence": 0, "finding": 0, "adr": 0,
    }
    assert load_yaml(project / "manifest.yaml")["counters"] == counters

    assert "Test run creado" in process("create-test-run", "--test-ref", "checks/smoke: opaque")
    deep_test = rfc3 / "test_run_000001"
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": deep_test.relative_to(project).as_posix()}
    before = snapshot(hactors_root / "projects")
    for command in ("create-task-run", "create-rfc-run", "create-plan-run", "create-test-run"):
        output = process(command, expected=1)
        assert "No se puede crear" in output and "test_run" in output
        assert snapshot(hactors_root / "projects") == before
    process("use-run", "--parent")
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": deepest}
    process("use-run", rfc1.relative_to(project).as_posix())
    process("create-test-run")
    first_test = rfc1 / "test_run_000002"
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": first_test.relative_to(project).as_posix()}
    process("use-run", "--parent")
    process("create-test-run", "--test-ref", "")
    sibling_test = rfc1 / "test_run_000003"
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": sibling_test.relative_to(project).as_posix()}
    for test, ref in ((deep_test, "checks/smoke: opaque"), (first_test, ""), (sibling_test, "")):
        assert load_yaml(test / "manifest.yaml")["identity"] == {"id": test.name, "test_ref": ref}
        assert list(test.iterdir()) == [test / "manifest.yaml"]
        originals[test / "manifest.yaml"] = (test / "manifest.yaml").read_bytes()
    counters["test_run"] = 3
    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    process("use-run", deep_test.relative_to(project).as_posix())
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": deep_test.relative_to(project).as_posix()}

    harness_ref, content_ref = "HRN-00001@v1", "content: 'opaque'\n# literal"
    assert "Harness run creado" in process(
        "create-harness-run", "--harness-ref", harness_ref, "--content-ref", content_ref,
    )
    deep_harness = deep_test / "harness_run_000001"
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": deep_harness.relative_to(project).as_posix()}
    before = snapshot(hactors_root / "projects")
    for command in ("create-task-run", "create-rfc-run", "create-plan-run", "create-test-run", "create-harness-run"):
        output = process(command, expected=1)
        assert "No se puede crear" in output and "dentro de un harness_run" in output
        assert snapshot(hactors_root / "projects") == before
    # Each subprocess must persist the complete repeated RFC/PLAN ancestry.
    for ancestor in reversed([*runs, deep_test]):
        process("use-run", "--parent")
        assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": ancestor.relative_to(project).as_posix()}
    process("use-run", "--parent")
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": ""}
    process("use-run", deep_test.relative_to(project).as_posix())
    process("create-harness-run", "--harness-ref", harness_ref, "--content-ref", content_ref)
    sibling_harness = deep_test / "harness_run_000002"
    process("use-run", first_test.relative_to(project).as_posix())
    process("create-harness-run", "--harness-ref", "", "--content-ref", "")
    initial_harness = first_test / "harness_run_000003"
    for run, hrn, content in (
        (deep_harness, harness_ref, content_ref), (sibling_harness, harness_ref, content_ref),
        (initial_harness, "", ""),
    ):
        assert load_yaml(run / "manifest.yaml") == {
            "identity": {"id": run.name, "harness_ref": hrn, "content_ref": content},
            "execution": {"source_revision": "", "parameters": {}},
            "state": {"status": "", "blocked_reason": ""},
        }
        assert list(run.iterdir()) == [run / "manifest.yaml"]
        originals[run / "manifest.yaml"] = (run / "manifest.yaml").read_bytes()
    counters["harness_run"] = 3
    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    process("use-run", deep_harness.relative_to(project).as_posix())
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": deep_harness.relative_to(project).as_posix()}

    process("use-run", plan1.relative_to(project).as_posix())
    process("create-rfc-run", "--rfc-ref", references[3])
    rfc4 = plan1 / "rfc_run_000004"
    assert load_yaml(rfc4 / "manifest.yaml")["identity"] == {"id": rfc4.name, "rfc_ref": references[3]}
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": rfc4.relative_to(project).as_posix()}
    counters["rfc_run"] = 4
    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    process("use-run", "--parent")
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": plan1.relative_to(project).as_posix()}
    originals[rfc4 / "manifest.yaml"] = (rfc4 / "manifest.yaml").read_bytes()
    before = snapshot(hactors_root / "projects")
    assert "No se puede crear" in process("create-plan-run", expected=1)
    assert "No se puede crear" in process("create-task-run", expected=1)
    assert snapshot(hactors_root / "projects") == before

    # Legacy context is rejected without implicit migration, even with empty fields.
    state_file.write_text(yaml.safe_dump({
        "active_project": "proj", "current_workflow_run": workflow.name,
        "current_task_run": "", "current_rfc_run": "",
    }))
    before = snapshot(hactors_root / "projects")
    for args in (
        ("create-workflow",), ("create-task-run",), ("create-rfc-run",), ("create-plan-run",),
        ("create-test-run",), ("create-harness-run",), ("use-run", deepest), ("use-run", "--parent"),
    ):
        output = process(*args, expected=1)
        assert "use-project" in output and "use-run" in output
        assert snapshot(hactors_root / "projects") == before
    branch_before = snapshot(project)
    process("use-project", "proj")
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": ""}
    process("use-run", deepest)
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": deepest}
    assert snapshot(project) == branch_before

    # Create a sibling task only after explicitly selecting its workflow.
    process("use-run", workflow.relative_to(project).as_posix())
    process("create-task-run")
    process("create-rfc-run", "--rfc-ref", "RFC-F00001")
    sibling_rfc = workflow / "task_run_000002" / "rfc_run_000005"
    assert (sibling_rfc / "manifest.yaml").is_file()
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": sibling_rfc.relative_to(project).as_posix()}
    process("create-workflow")
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": "hactors/workflow_run_000002"}
    before = snapshot(hactors_root / "projects")
    assert "No se puede crear" in process("create-rfc-run", expected=1)
    assert snapshot(hactors_root / "projects") == before
    counters.update(workflow_run=2, task_run=2, rfc_run=5)
    assert load_yaml(project / "manifest.yaml")["counters"] == counters

    process("create-project", "other")
    process("use-project", "other")
    assert load_yaml(state_file) == {"active_project": "other", "active_run_path": ""}
    before = snapshot(hactors_root / "projects")
    assert "No hay instancia activa" in process("create-plan-run", expected=1)
    assert "manifest" in process("use-run", deepest, expected=1).lower()
    assert snapshot(hactors_root / "projects") == before
    assert all(value == 0 for value in load_yaml(hactors_root / "projects" / "other" / "manifest.yaml")["counters"].values())
    for command in ("create-workflow", "create-task-run", "create-rfc-run", "create-test-run"):
        process(command)
    other_path = "hactors/workflow_run_000001/task_run_000001/rfc_run_000001/test_run_000001"
    assert load_yaml(state_file) == {"active_project": "other", "active_run_path": other_path}
    assert load_yaml(hactors_root / "projects" / "other" / "manifest.yaml")["counters"] == {
        "task": 0, "workflow_run": 1, "task_run": 1, "rfc_run": 1, "plan_run": 0,
        "test_run": 1, "harness_run": 0, "evidence": 0, "finding": 0, "adr": 0,
    }
    process("create-harness-run")
    other_path += "/harness_run_000001"
    assert load_yaml(state_file) == {"active_project": "other", "active_run_path": other_path}
    assert load_yaml(hactors_root / "projects" / "other" / "manifest.yaml")["counters"] == {
        "task": 0, "workflow_run": 1, "task_run": 1, "rfc_run": 1, "plan_run": 0,
        "test_run": 1, "harness_run": 1, "evidence": 0, "finding": 0, "adr": 0,
    }
    assert load_yaml(hactors_root / "projects" / "other" / other_path / "manifest.yaml") == {
        "identity": {"id": "harness_run_000001", "harness_ref": "", "content_ref": ""},
        "execution": {"source_revision": "", "parameters": {}},
        "state": {"status": "", "blocked_reason": ""},
    }
    process("use-project", "proj")
    process("use-run", deepest)
    assert load_yaml(state_file) == {"active_project": "proj", "active_run_path": deepest}
    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    assert all(path.read_bytes() == content for path, content in originals.items())
    assert snapshot(hactors_root / "specs" / "templates") == source_templates
