import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.project import create_project
from hactors_cli.core.state import load_state, set_active_run
from hactors_cli.core.task import TaskError, create_task, normalize_task_ref
from hactors_cli.core.task_run import create_task_run
from hactors_cli.core.workflow import WorkflowError, create_workflow

SPECS_TEMPLATES = Path(__file__).resolve().parents[3] / "specs" / "templates"

TEMPLATE_DEFAULTS = {
    "task": "",
    "rfcs": [],
    "required_knowledge": {"index": "specs/INDEX_SPECS.md", "from_affected_modules": [], "additional": []},
    "actor": "",
    "deliverables": [],
    "acceptance_criteria": {"scope": "full", "criteria": []},
    "execution": {"status": "draft", "target_status": "done", "evidence": [], "blockers": []},
}

REFERENCE = "Estructura y campos: `specs/templates/TASK_TEMPLATE.md`.\n"


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


def front_matter(path):
    text = path.read_text()
    assert text.startswith("---\n")
    header, body = text.removeprefix("---\n").split("\n---\n", 1)
    return yaml.safe_load(header), body.removeprefix("\n")


def expected_task(**overrides):
    data = yaml.safe_load(yaml.safe_dump(TEMPLATE_DEFAULTS))
    data.update(overrides)
    return data


@pytest.fixture
def project(hactors_root):
    return create_project("proj", hactors_root)


def test_task_template_matches_the_normative_schema(hactors_root, load_yaml):
    template = load_yaml(hactors_root / "specs" / "templates" / "task_template.yaml")
    assert template == TEMPLATE_DEFAULTS
    normative = (SPECS_TEMPLATES / "TASK_TEMPLATE.md").read_text()
    block = normative.split("# Plantilla de TASK", 1)[1].split("```yaml\n", 1)[1].split("```", 1)[0]
    assert yaml.safe_load(block) == template


def test_task_file_is_markdown_with_a_frontmatter_and_a_reference(hactors_root, project):
    task_id, path = create_task(hactors_root, project.name)
    header, body = front_matter(path)
    assert list(header) == list(TEMPLATE_DEFAULTS)
    assert header == expected_task()
    assert body == REFERENCE
    assert path.suffix == ".md"
    assert task_id == "TASK-00001"


def test_first_task_consumes_only_its_own_counter(hactors_root, project, load_yaml):
    before = snapshot(hactors_root)
    manifest_before = load_yaml(project / "manifest.yaml")

    task_id, path = create_task(hactors_root, project.name, task="Migrar el módulo")

    assert task_id == "TASK-00001"
    assert path == project / "tasks" / "TASK-00001.md"
    assert front_matter(path)[0] == expected_task(task="Migrar el módulo")
    expected_manifest = yaml.safe_load(yaml.safe_dump(manifest_before))
    expected_manifest["counters"]["task"] = 1
    assert load_yaml(project / "manifest.yaml") == expected_manifest
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {path.relative_to(hactors_root).as_posix()}
    assert before.keys() - after.keys() == set()
    assert [p for p in before if before[p] != after[p]] == ["projects/proj/manifest.yaml"]


def test_task_ids_are_sequential_across_the_project(hactors_root, project, load_yaml):
    paths = [create_task(hactors_root, project.name)[1] for _ in range(3)]
    assert [path.name for path in paths] == [f"TASK-{index:05d}.md" for index in range(1, 4)]
    assert {path.parent for path in paths} == {project / "tasks"}
    assert len({path.stat().st_ino for path in paths}) == 3
    assert load_yaml(project / "manifest.yaml")["counters"]["task"] == 3


def test_task_counter_is_independent_of_run_counters(hactors_root, project, load_yaml):
    create_task(hactors_root, project.name)
    counters = load_yaml(project / "manifest.yaml")["counters"]
    assert counters["task"] == 1
    assert counters["task_run"] == 0

    workflow = create_workflow(hactors_root, project.name)
    create_task_run(hactors_root, project.name, workflow.relative_to(project).as_posix())
    counters = load_yaml(project / "manifest.yaml")["counters"]
    assert counters["task"] == 1
    assert counters["workflow_run"] == counters["task_run"] == 1


@pytest.mark.parametrize("field,value", [
    ("task", "Ejecutar el alcance acordado"),
    ("actor", "[actor: human | agent]"),
])
def test_explicit_options_override_only_their_own_field(hactors_root, project, field, value):
    _, path = create_task(hactors_root, project.name, **{field: value})
    assert front_matter(path)[0] == expected_task(**{field: value})


@pytest.mark.parametrize("kwargs", [
    {}, {"task": ""}, {"actor": ""}, {"task": "", "actor": ""},
    {"task": "t", "actor": "[actor: agent]"},
])
def test_template_defaults_are_preserved_unless_a_value_is_explicit(hactors_root, project, kwargs):
    source = hactors_root / "specs" / "templates" / "task_template.yaml"
    template = expected_task(task="título de la plantilla", actor="[actor: human]")
    template["rfcs"] = ["RFC-A00001"]
    template["deliverables"] = ["entregable"]
    template["required_knowledge"]["additional"] = ["specs/RFC.md"]
    template["acceptance_criteria"] = {"scope": "partial", "criteria": ["C-1"]}
    template["execution"]["status"] = "approved"
    source.write_text(yaml.safe_dump(template))
    original_bytes = source.read_bytes()

    _, path = create_task(hactors_root, project.name, **kwargs)

    expected = yaml.safe_load(yaml.safe_dump(template))
    expected.update(kwargs)
    assert front_matter(path)[0] == expected
    assert source.read_bytes() == original_bytes


@pytest.mark.parametrize("value", [
    "actor-inventado", "ayer", "  espaciado  ", "línea: 'uno'\nsegunda # literal",
    "$(touch ejecutado); ./receta.py", "../../../fuera", "42", "null", "[]",
])
def test_declared_values_are_stored_verbatim_without_validation(hactors_root, project, value):
    _, path = create_task(hactors_root, project.name, task=value, actor=value)
    header = front_matter(path)[0]
    assert header["task"] == header["actor"] == value
    assert not (project / "ejecutado").exists()


def test_nested_blocks_always_come_from_the_template(hactors_root, project):
    _, path = create_task(hactors_root, project.name, task="t", actor="a")
    header = front_matter(path)[0]
    assert header["rfcs"] == []
    assert header["deliverables"] == []
    assert header["required_knowledge"] == TEMPLATE_DEFAULTS["required_knowledge"]
    assert header["acceptance_criteria"] == TEMPLATE_DEFAULTS["acceptance_criteria"]
    assert header["execution"] == TEMPLATE_DEFAULTS["execution"]
    help_output = CliRunner().invoke(cli, ["create-task", "--help"]).output
    for absent in ("--rfcs", "--status", "--target-status", "--deliverables", "--scope", "--id"):
        assert absent not in help_output


def test_creation_never_changes_the_active_selection(hactors_root, project):
    workflow = create_workflow(hactors_root, project.name)
    run = create_task_run(hactors_root, project.name, workflow.relative_to(project).as_posix())
    origin = run.relative_to(project).as_posix()
    set_active_run(hactors_root, project.name, origin)
    state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()

    create_task(hactors_root, project.name)

    assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before
    assert load_state(hactors_root)["active_run_path"] == origin


@pytest.mark.parametrize("kind", ["file", "directory", "symlink"])
def test_existing_task_is_never_overwritten_nor_counted(hactors_root, project, tmp_path, load_yaml, kind):
    target = project / "tasks" / "TASK-00001.md"
    if kind == "file":
        target.write_text("task: manual\nno: sobrescribir\n")
    elif kind == "directory":
        target.mkdir()
        (target / "manual.md").write_text("manual\n")
    else:
        outside = tmp_path / "fuera.md"
        outside.write_text("manual\n")
        target.symlink_to(outside)
    before = snapshot(tmp_path)

    with pytest.raises(TaskError, match="Ya existe una TASK"):
        create_task(hactors_root, project.name)

    assert snapshot(tmp_path) == before
    assert load_yaml(project / "manifest.yaml")["counters"]["task"] == 0

    if kind == "file":
        target.unlink()
        create_task(hactors_root, project.name)
        assert load_yaml(project / "manifest.yaml")["counters"]["task"] == 1


@pytest.mark.parametrize("value", [-1, True, False, 1.5, "1", None, [], {}])
def test_invalid_counter_is_rejected_before_any_write(hactors_root, project, load_yaml, value):
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"]["task"] = value
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)
    with pytest.raises(TaskError, match="Contador inválido"):
        create_task(hactors_root, project.name)
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("value", [None, [], "inválido", 1, False])
def test_invalid_counters_mapping_is_rejected_before_any_write(hactors_root, project, load_yaml, value):
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"] = value
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)
    with pytest.raises(TaskError, match="Contadores inválidos"):
        create_task(hactors_root, project.name)
    assert snapshot(hactors_root) == before


def test_missing_counter_is_added_starting_at_one(hactors_root, project, load_yaml):
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"].pop("task")
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)

    task_id, path = create_task(hactors_root, project.name)

    assert task_id == "TASK-00001"
    data["counters"]["task"] = 1
    assert load_yaml(manifest) == data
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {path.relative_to(hactors_root).as_posix()}
    assert {p for p in before if before[p] != after[p]} == {"projects/proj/manifest.yaml"}


def test_missing_tasks_directory_is_rejected_without_writes(hactors_root, project):
    directory = project / "tasks"
    for entry in directory.iterdir():
        entry.unlink()
    directory.rmdir()
    before = snapshot(hactors_root)
    with pytest.raises(TaskError, match="no existe"):
        create_task(hactors_root, project.name)
    assert snapshot(hactors_root) == before


def test_symlinked_tasks_directory_is_rejected(hactors_root, project, tmp_path):
    target = tmp_path / "tasks-reales"
    (project / "tasks").rename(target)
    (project / "tasks").symlink_to(target, target_is_directory=True)
    before = snapshot(tmp_path)
    with pytest.raises(TaskError, match="no existe"):
        create_task(hactors_root, project.name)
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("problem", ["missing", "broken", "non-mapping"])
def test_template_problems_are_reported_without_writes(hactors_root, project, problem):
    template_path = hactors_root / "specs" / "templates" / "task_template.yaml"
    if problem == "missing":
        template_path.unlink()
    elif problem == "broken":
        template_path.write_text("task: [roto\n")
    else:
        template_path.write_text("[]\n")
    before = snapshot(hactors_root)
    with pytest.raises(TaskError):
        create_task(hactors_root, project.name)
    assert snapshot(hactors_root) == before


def test_cli_help_documents_the_declared_fields():
    runner = CliRunner()
    assert "create-task" in runner.invoke(cli, ["--help"]).output
    result = runner.invoke(cli, ["create-task", "--help"])
    assert result.exit_code == 0
    for option in ("--task", "--actor", "--root"):
        assert option in result.output
    assert "literalmente" in " ".join(result.output.split())


def test_cli_requires_active_project(hactors_root, project):
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-task", expected=1)
    assert "No hay proyecto activo" in result.output
    assert "use-project" in result.output
    assert snapshot(hactors_root) == before


def test_cli_creates_a_task_usable_as_task_ref(hactors_root, project, load_yaml):
    invoke(hactors_root, "use-project", project.name)
    state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()

    result = invoke(hactors_root, "create-task", "--task", "Cerrar el alcance", "--actor", "[actor: human]")

    assert "TASK-00001" in result.output
    assert str(project / "tasks" / "TASK-00001.md") in result.output
    assert front_matter(project / "tasks" / "TASK-00001.md")[0] == expected_task(
        task="Cerrar el alcance", actor="[actor: human]",
    )
    assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before

    invoke(hactors_root, "create-workflow", "--task-ref", "TASK-00001")
    manifest = load_yaml(project / "hactors" / "workflow_run_000001" / "manifest.yaml")
    assert manifest["workflow_run_000001"]["identity"]["task_ref"] == "TASK-00001"


@pytest.mark.parametrize("task_ref,expected", [
    ("", ""),
    ("TASK-00001", "TASK-00001"),
    ("tasks/TASK-00001.md", "TASK-00001"),
    ("TASK-100000", "TASK-100000"),
    ("tasks/TASK-100000.md", "TASK-100000"),
])
def test_task_ref_is_normalized_to_the_bare_identifier(task_ref, expected):
    assert normalize_task_ref(task_ref) == expected


@pytest.mark.parametrize("task_ref", [
    "task_000001", "tasks/task_000001.md", "TASK-00001.md", "tasks/TASK-00001",
    "tasks/sub/TASK-00001.md", "tasks/tasks/TASK-00001.md", "/tmp/tasks/TASK-00001.md",
    "../tasks/TASK-00001.md", "TASK-0001", "task-00001", "TASK_00001",
    " TASK-00001", "TASK-00001 ", "rfcs/RFC-A00001.md",
])
def test_any_other_task_ref_form_is_rejected(task_ref):
    with pytest.raises(ValueError, match="Referencia de TASK inválida"):
        normalize_task_ref(task_ref)


@pytest.mark.parametrize("task_ref", ["TASK-00001", "tasks/TASK-00001.md"])
def test_create_workflow_records_the_identifier_for_both_forms(
    hactors_root, project, load_yaml, task_ref
):
    (project / "tasks" / "TASK-00001.md").write_text("# TASK\n")

    workflow = create_workflow(hactors_root, project.name, task_ref=task_ref)

    manifest = load_yaml(workflow / "manifest.yaml")
    assert manifest[workflow.name]["identity"]["task_ref"] == "TASK-00001"


def test_create_workflow_rejects_an_invalid_task_ref_before_any_write(hactors_root, project):
    before = snapshot(hactors_root)

    with pytest.raises(WorkflowError, match="Referencia de TASK inválida"):
        create_workflow(hactors_root, project.name, task_ref="task_000001")

    assert snapshot(hactors_root) == before


def test_cli_reports_an_invalid_task_ref_without_creating_the_run(hactors_root, project):
    invoke(hactors_root, "use-project", project.name)
    before = snapshot(hactors_root)

    result = invoke(hactors_root, "create-workflow", "--task-ref", "task_000001", expected=1)

    output = " ".join(result.output.split())
    assert "Referencia de TASK inválida: 'task_000001'" in output
    assert "'TASK-00001'" in output and "'tasks/TASK-00001.md'" in output
    assert snapshot(hactors_root) == before


def test_cli_help_documents_the_accepted_task_ref_forms():
    output = " ".join(CliRunner().invoke(cli, ["create-workflow", "--help"]).output.split())
    assert "--task-ref" in output
    assert "TASK-00001" in output and "tasks/TASK-00001.md" in output


def test_cli_root_is_autodetected_from_the_working_directory(hactors_root, project, monkeypatch):
    invoke(hactors_root, "use-project", project.name)
    monkeypatch.chdir(project / "tasks")

    result = CliRunner().invoke(cli, ["create-task", "--task", "Desde el directorio"])

    assert result.exit_code == 0, result.output
    assert front_matter(project / "tasks" / "TASK-00001.md")[0] == expected_task(
        task="Desde el directorio",
    )


def test_cli_process_creates_tasks_in_a_separate_process(hactors_root, project):
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]), PYTHONDONTWRITEBYTECODE="1")

    def process(*args, expected=0):
        result = subprocess.run(
            [sys.executable, "-m", "hactors_cli", *args, "--root", str(hactors_root)],
            capture_output=True, text=True, env=env, check=False,
        )
        assert result.returncode == expected, result.stdout + result.stderr
        return result.stdout

    process("use-project", project.name)
    before = snapshot(hactors_root)
    assert "TASK-00001" in process("create-task", "--task", "Primera")
    assert "TASK-00002" in process("create-task", "--actor", "[actor: agent]")
    assert front_matter(project / "tasks" / "TASK-00001.md")[0] == expected_task(task="Primera")
    assert front_matter(project / "tasks" / "TASK-00002.md")[0] == expected_task(actor="[actor: agent]")
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {
        "projects/proj/tasks/TASK-00001.md", "projects/proj/tasks/TASK-00002.md",
    }
    assert [p for p in before if before[p] != after[p]] == ["projects/proj/manifest.yaml"]
