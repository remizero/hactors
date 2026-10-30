import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.harness_run import create_harness_run
from hactors_cli.core.project import create_project
from hactors_cli.core.state import load_state, set_active_run
from hactors_cli.core.summary import SummaryError, create_summary
from hactors_cli.core.test_run import create_test_run

SPECS_TEMPLATES = Path(__file__).resolve().parents[3] / "specs" / "templates"

TEMPLATE_DEFAULTS = {
    "artifact": "",
    "title": "",
    "level": "",
    "status": "in-progress",
    "final_state": "",
    "target_state": "",
    "date": "",
}

REFERENCE = "Estructura y secciones: `specs/templates/SUMMARY_TEMPLATE.md`.\n"


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


def expected_summary(level, artifact, **overrides):
    data = dict(TEMPLATE_DEFAULTS)
    data["artifact"] = artifact
    data["level"] = level
    data.update(overrides)
    return data


@pytest.fixture
def artifacts(hactors_root):
    project = create_project("proj", hactors_root)
    (project / "rfcs" / "RFC-A00001.md").write_text("# RFC original\n")
    (project / "tasks" / "TASK-00001.md").write_text("# TASK original\n")
    (project / "standards" / "GIT.md").write_text("# GIT original\n")
    return project


@pytest.fixture
def harness_origin(hactors_root, rfc_parent):
    project, ancestors = rfc_parent
    test = create_test_run(hactors_root, project.name, ancestors[-1].relative_to(project).as_posix())
    harness = create_harness_run(hactors_root, project.name, test.relative_to(project).as_posix())
    return project, [*ancestors, test, harness]


def test_summary_template_matches_the_normative_header(hactors_root, load_yaml):
    template = load_yaml(hactors_root / "specs" / "templates" / "summary_template.yaml")
    assert template == TEMPLATE_DEFAULTS
    normative = (SPECS_TEMPLATES / "SUMMARY_TEMPLATE.md").read_text()
    block = normative.split("## Cabecera\n\n```yaml\n", 1)[1].split("```", 1)[0]
    assert yaml.safe_load(block) == template


def test_summary_file_is_markdown_with_a_frontmatter_and_a_reference(hactors_root, artifacts):
    path = create_summary(hactors_root, artifacts.name, "rfcs/RFC-A00001.md")
    header, body = front_matter(path)
    assert list(header) == list(TEMPLATE_DEFAULTS)
    assert body == REFERENCE
    assert path.suffix == ".md"


@pytest.mark.parametrize("name", [
    "RFC-A00001.md",
    "RFC-A00001 — nombre-descriptivo.md",
    "RFC-F00002 - con espacios.md",
    "RFC-T00003-MOD00001.md",
    "RFC-I00004.v2.md",
])
def test_rfc_summary_is_named_after_the_rfc_without_its_extension(hactors_root, artifacts, name):
    project = artifacts
    (project / "rfcs" / name).write_text("# RFC\n")

    path = create_summary(hactors_root, project.name, f"rfcs/{name}")

    assert path == project / "rfcs" / f"{Path(name).stem} - Summary.md"
    assert front_matter(path)[0] == expected_summary("rfc", f"rfcs/{name}")


def test_rfc_origin_adds_only_the_summary_and_touches_nothing_else(hactors_root, artifacts, load_yaml):
    project = artifacts
    before = snapshot(hactors_root)
    manifest_before = load_yaml(project / "manifest.yaml")

    path = create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md", title="Resultado")

    assert path == project / "rfcs" / "RFC-A00001 - Summary.md"
    assert front_matter(path)[0] == expected_summary("rfc", "rfcs/RFC-A00001.md", title="Resultado")
    assert (project / "rfcs" / "RFC-A00001.md").read_text() == "# RFC original\n"
    assert load_yaml(project / "manifest.yaml") == manifest_before
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {path.relative_to(hactors_root).as_posix()}
    assert before.keys() - after.keys() == set()
    assert [p for p in before if before[p] != after[p]] == []


def test_workflow_run_origin_creates_summary_md_next_to_its_manifest(hactors_root, artifacts, load_yaml):
    project = artifacts
    invoke(hactors_root, "use-project", project.name)
    invoke(hactors_root, "create-workflow", "--task-ref", "TASK-00001")
    run = project / "hactors" / "workflow_run_000001"
    manifest_before = (run / "manifest.yaml").read_bytes()
    before = snapshot(hactors_root)

    path = create_summary(hactors_root, project.name, "hactors/workflow_run_000001")

    assert path == run / "SUMMARY.md"
    assert front_matter(path)[0] == expected_summary("workflow_run", "hactors/workflow_run_000001")
    assert (run / "manifest.yaml").read_bytes() == manifest_before
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {path.relative_to(hactors_root).as_posix()}
    assert [p for p in before if before[p] != after[p]] == []


def test_no_counter_is_consumed_by_a_summary(hactors_root, harness_origin, load_yaml):
    project, ancestors = harness_origin
    (project / "rfcs" / "RFC-A00001.md").write_text("# RFC\n")
    counters = load_yaml(project / "manifest.yaml")["counters"].copy()

    create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md")
    create_summary(hactors_root, project.name, ancestors[0].relative_to(project).as_posix())

    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    assert "summary" not in counters


def test_intermediate_instances_have_no_summary_of_their_own(hactors_root, harness_origin):
    project, ancestors = harness_origin
    before = snapshot(hactors_root)

    for run in ancestors[1:]:
        with pytest.raises(SummaryError, match="Solo un workflow_run"):
            create_summary(hactors_root, project.name, run.relative_to(project).as_posix())

    assert snapshot(hactors_root) == before
    assert not [path for run in ancestors[1:] for path in run.glob("SUMMARY.md")]


@pytest.mark.parametrize("origin", [
    "tasks/TASK-00001.md",
    "standards/GIT.md",
    "project.yaml",
    "manifest.yaml",
    "rfcs",
    "hactors",
])
def test_artifact_origins_outside_rfcs_are_rejected(hactors_root, artifacts, origin):
    project = artifacts
    (project / "rfcs" / "anidado").mkdir()
    (project / "rfcs" / "anidado" / "RFC-A00002.md").write_text("# RFC\n")
    before = snapshot(hactors_root)

    with pytest.raises(SummaryError):
        create_summary(hactors_root, project.name, origin)

    assert snapshot(hactors_root) == before


def test_rfc_origin_must_be_a_file_inside_rfcs(hactors_root, artifacts):
    project = artifacts
    (project / "rfcs" / "anidado").mkdir()
    (project / "rfcs" / "anidado" / "RFC-A00002.md").write_text("# RFC\n")
    before = snapshot(hactors_root)

    with pytest.raises(SummaryError, match="junto a su archivo"):
        create_summary(hactors_root, project.name, "rfcs/anidado")
    with pytest.raises(SummaryError, match="junto a su archivo"):
        create_summary(hactors_root, project.name, "rfcs/anidado/RFC-A00002.md")

    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("field,value", [
    ("title", "Resultado alcanzado"),
    ("status", "consolidated"),
    ("final_state", "closed"),
    ("target_state", "closed"),
    ("date", "2026-10-30"),
])
def test_explicit_options_override_only_their_own_field(hactors_root, artifacts, field, value):
    project = artifacts
    path = create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md", **{field: value})
    assert front_matter(path)[0] == expected_summary(
        "rfc", "rfcs/RFC-A00001.md", **{field: value}
    )


@pytest.mark.parametrize("kwargs", [
    {}, {"title": ""}, {"status": ""}, {"final_state": ""}, {"target_state": ""}, {"date": ""},
    {"title": "", "status": "", "final_state": "", "target_state": "", "date": ""},
    {"title": "t", "status": "in-progress", "final_state": "closed",
     "target_state": "closed", "date": "2026-10-30"},
])
def test_template_defaults_are_preserved_unless_a_value_is_explicit(hactors_root, artifacts, kwargs):
    project = artifacts
    source = hactors_root / "specs" / "templates" / "summary_template.yaml"
    template = dict(TEMPLATE_DEFAULTS)
    template.update(
        title="título de la plantilla", status="consolidated", final_state="cerrado",
        target_state="cerrado", date="1999-01-01",
    )
    source.write_text(yaml.safe_dump(template))
    original_bytes = source.read_bytes()

    path = create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md", **kwargs)

    expected = dict(template, artifact="rfcs/RFC-A00001.md", level="rfc")
    expected.update(kwargs)
    assert front_matter(path)[0] == expected
    assert source.read_bytes() == original_bytes


@pytest.mark.parametrize("value", [
    "estado-inventado", "ayer", "  espaciado  ", "línea: 'uno'\nsegunda # literal",
    "$(touch ejecutado); ./receta.py", "../../../fuera", "42", "null", "[]",
])
def test_declared_values_are_stored_verbatim_without_validation(hactors_root, artifacts, value):
    project = artifacts
    path = create_summary(
        hactors_root, project.name, "rfcs/RFC-A00001.md",
        title=value, status=value, final_state=value, target_state=value, date=value,
    )
    header = front_matter(path)[0]
    assert header["title"] == header["status"] == header["final_state"] == value
    assert header["target_state"] == header["date"] == value
    assert not (project / "ejecutado").exists()


def test_artifact_and_level_are_derived_from_the_origin(hactors_root, artifacts):
    project = artifacts
    path = create_summary(
        hactors_root, project.name, "rfcs/RFC-A00001.md", title="x", status="y",
    )
    header = front_matter(path)[0]
    assert header["artifact"] == "rfcs/RFC-A00001.md"
    assert header["level"] == "rfc"
    help_output = CliRunner().invoke(cli, ["create-summary", "--help"]).output
    assert "--artifact" not in help_output
    assert "--level" not in help_output


def test_previous_summaries_are_never_rewritten(hactors_root, artifacts, load_yaml):
    project = artifacts
    (project / "rfcs" / "RFC-F00002.md").write_text("# RFC segunda\n")

    first = create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md", title="primero")
    first_bytes = first.read_bytes()
    second = create_summary(hactors_root, project.name, "rfcs/RFC-F00002.md", title="segundo")

    assert first.read_bytes() == first_bytes
    assert second != first
    assert front_matter(first)[0] == expected_summary("rfc", "rfcs/RFC-A00001.md", title="primero")
    assert front_matter(second)[0] == expected_summary("rfc", "rfcs/RFC-F00002.md", title="segundo")


@pytest.mark.parametrize("kind", ["file", "directory", "symlink"])
def test_existing_summary_is_never_overwritten(hactors_root, artifacts, tmp_path, kind):
    project = artifacts
    target = project / "rfcs" / "RFC-A00001 - Summary.md"
    if kind == "file":
        target.write_text("artifact: manual\nno: sobrescribir\n")
    elif kind == "directory":
        target.mkdir()
        (target / "manual.md").write_text("manual\n")
    else:
        outside = tmp_path / "fuera.md"
        outside.write_text("manual\n")
        target.symlink_to(outside)
    before = snapshot(tmp_path)

    with pytest.raises(SummaryError, match="Ya existe un resumen"):
        create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md")

    assert snapshot(tmp_path) == before


def test_existing_workflow_summary_is_never_overwritten(hactors_root, artifacts):
    project = artifacts
    invoke(hactors_root, "use-project", project.name)
    invoke(hactors_root, "create-workflow", "--task-ref", "TASK-00001")
    summary = project / "hactors" / "workflow_run_000001" / "SUMMARY.md"
    summary.write_text("artifact: manual\n")
    before = snapshot(hactors_root)

    with pytest.raises(SummaryError, match="Ya existe un resumen"):
        create_summary(hactors_root, project.name, "hactors/workflow_run_000001")

    assert snapshot(hactors_root) == before


def test_creation_never_changes_the_active_selection(hactors_root, harness_origin):
    project, ancestors = harness_origin
    for index, run in enumerate((ancestors[-1], ancestors[-2], ancestors[0])):
        origin = run.relative_to(project).as_posix()
        rfc = f"rfcs/RFC-A0000{index + 1}.md"
        (project / rfc).write_text("# RFC\n")
        set_active_run(hactors_root, project.name, origin)
        state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()
        create_summary(hactors_root, project.name, rfc)
        assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before
        assert load_state(hactors_root)["active_run_path"] == origin


@pytest.mark.parametrize("origin", [
    "", "   ", "/tmp/fuera", "../fuera", "rfcs/../rfcs", ".", "./rfcs", "rfcs/.", "..",
    "rfcs//RFC-A00001.md", "rfcs/", "/rfcs/RFC-A00001.md", "rfcs\\RFC-A00001.md",
    "hactors/", "missing.md", "rfcs/missing.md",
    "hactors/workflow_run_999999", "hactors/workflow_run_1",
    "hactors/workflow_run_000001/harness_run_000001",
    "hactors/workflow_run_000001/task_run_000001/rfc_run_000001/harness_run_000001",
    "hactors/workflow_run_000001/task_run_000001/rfc_run_000001/test_run_000001/manifest.yaml",
    None, 42, [],
])
def test_invalid_origins_are_rejected_without_side_effects(hactors_root, harness_origin, origin):
    project, ancestors = harness_origin
    (project / "rfcs" / "RFC-A00001.md").write_text("# RFC\n")
    before = snapshot(hactors_root)
    with pytest.raises(SummaryError):
        create_summary(hactors_root, project.name, origin)
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("escape", [False, True], ids=["internal", "external"])
def test_symlinked_origin_is_rejected_without_writing_target(hactors_root, artifacts, tmp_path, escape):
    project = artifacts
    original = project / "rfcs" / "RFC-A00001.md"
    target = (tmp_path if escape else project / "rfcs") / "original.md"
    original.rename(target)
    original.symlink_to(target)
    before = snapshot(tmp_path)
    with pytest.raises(SummaryError, match="enlaces simbólicos"):
        create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("problem", ["missing", "broken", "non-mapping"])
def test_template_problems_are_reported_without_writes(hactors_root, artifacts, problem):
    project = artifacts
    template_path = hactors_root / "specs" / "templates" / "summary_template.yaml"
    if problem == "missing":
        template_path.unlink()
    elif problem == "broken":
        template_path.write_text("artifact: [roto\n")
    else:
        template_path.write_text("[]\n")
    before = snapshot(hactors_root)
    with pytest.raises(SummaryError):
        create_summary(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert snapshot(hactors_root) == before


def test_cli_help_documents_origin_and_declared_fields():
    runner = CliRunner()
    assert "create-summary" in runner.invoke(cli, ["--help"]).output
    result = runner.invoke(cli, ["create-summary", "--help"])
    assert result.exit_code == 0
    for option in (
        "--origin", "--title", "--status", "--final-state", "--target-state", "--date", "--root",
    ):
        assert option in result.output
    assert "workflow_run de la instancia activa" in " ".join(result.output.split())


def test_cli_requires_active_project(hactors_root, artifacts):
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-summary", "--origin", "rfcs/RFC-A00001.md", expected=1)
    assert "No hay proyecto activo" in result.output
    assert "use-project" in result.output
    assert snapshot(hactors_root) == before


def test_cli_without_origin_requires_an_active_run(hactors_root, artifacts):
    project = artifacts
    invoke(hactors_root, "use-project", project.name)
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-summary", expected=1)
    assert "No hay instancia activa" in result.output
    assert snapshot(hactors_root) == before


def test_cli_defaults_origin_to_the_active_workflow_run_at_any_depth(hactors_root, harness_origin):
    project, ancestors = harness_origin
    invoke(hactors_root, "use-project", project.name)
    workflow = ancestors[0].relative_to(project).as_posix()
    summary = ancestors[0] / "SUMMARY.md"

    for run in ancestors:
        origin = run.relative_to(project).as_posix()
        invoke(hactors_root, "use-run", origin)
        state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()
        summary.unlink(missing_ok=True)

        result = invoke(hactors_root, "create-summary")

        assert str(summary) in result.output
        assert front_matter(summary)[0] == expected_summary("workflow_run", workflow)
        assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before
        assert load_state(hactors_root)["active_run_path"] == origin
        assert sorted(
            path.relative_to(project).as_posix()
            for path in (project / "hactors").rglob("SUMMARY.md")
        ) == [f"{workflow}/SUMMARY.md"]


def test_cli_creates_summaries_at_both_levels(hactors_root, artifacts):
    project = artifacts
    invoke(hactors_root, "use-project", project.name)
    invoke(hactors_root, "create-workflow", "--task-ref", "TASK-00001")
    state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()

    invoke(
        hactors_root, "create-summary", "--origin", "rfcs/RFC-A00001.md",
        "--title", "Resultado de la RFC", "--status", "consolidated",
        "--final-state", "closed", "--target-state", "closed", "--date", "2026-10-30",
    )
    assert front_matter(project / "rfcs" / "RFC-A00001 - Summary.md")[0] == expected_summary(
        "rfc", "rfcs/RFC-A00001.md", title="Resultado de la RFC", status="consolidated",
        final_state="closed", target_state="closed", date="2026-10-30",
    )

    result = invoke(
        hactors_root, "create-summary", "--origin", "hactors/workflow_run_000001",
        "--title", "Resultado global",
    )
    assert str(project / "hactors" / "workflow_run_000001" / "SUMMARY.md") in result.output
    assert front_matter(project / "hactors" / "workflow_run_000001" / "SUMMARY.md")[0] == (
        expected_summary(
            "workflow_run", "hactors/workflow_run_000001", title="Resultado global",
        )
    )
    assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before


@pytest.mark.parametrize("args,message", [
    (("--origin", "rfcs/missing.md"), "no encontrado"),
    (("--origin", "tasks/TASK-00001.md"), "junto a su archivo"),
    (("--origin", "../fuera"), "Origen inválido"),
    (("--origin", "hactors"), "Origen inválido"),
    (("--origin", ""), "Origen inválido"),
])
def test_cli_reports_invalid_origin_without_writes(hactors_root, artifacts, args, message):
    project = artifacts
    invoke(hactors_root, "use-project", project.name)
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-summary", *args, expected=1)
    assert message in result.output
    assert snapshot(hactors_root) == before


def test_cli_root_is_autodetected_from_the_working_directory(hactors_root, artifacts, monkeypatch):
    project = artifacts
    invoke(hactors_root, "use-project", project.name)
    monkeypatch.chdir(project / "rfcs")

    result = CliRunner().invoke(cli, ["create-summary", "--origin", "rfcs/RFC-A00001.md"])

    assert result.exit_code == 0, result.output
    assert front_matter(project / "rfcs" / "RFC-A00001 - Summary.md")[0] == expected_summary(
        "rfc", "rfcs/RFC-A00001.md",
    )


def test_cli_process_creates_summaries_in_a_separate_process(hactors_root, artifacts):
    project = artifacts
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]), PYTHONDONTWRITEBYTECODE="1")

    def process(*args, expected=0):
        result = subprocess.run(
            [sys.executable, "-m", "hactors_cli", *args, "--root", str(hactors_root)],
            capture_output=True, text=True, env=env, check=False,
        )
        assert result.returncode == expected, result.stdout + result.stderr
        return result.stdout

    process("use-project", project.name)
    process("create-workflow", "--task-ref", "TASK-00001")
    before = snapshot(hactors_root)
    assert "Resumen creado en" in process(
        "create-summary", "--origin", "rfcs/RFC-A00001.md", "--title", "Uno",
    )
    assert "Resumen creado en" in process(
        "create-summary", "--origin", "hactors/workflow_run_000001", "--title", "Global",
    )
    assert front_matter(project / "rfcs" / "RFC-A00001 - Summary.md")[0] == expected_summary(
        "rfc", "rfcs/RFC-A00001.md", title="Uno",
    )
    assert front_matter(project / "hactors" / "workflow_run_000001" / "SUMMARY.md")[0] == (
        expected_summary("workflow_run", "hactors/workflow_run_000001", title="Global")
    )
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {
        "projects/proj/rfcs/RFC-A00001 - Summary.md",
        "projects/proj/hactors/workflow_run_000001/SUMMARY.md",
    }
    assert [p for p in before if before[p] != after[p]] == []
