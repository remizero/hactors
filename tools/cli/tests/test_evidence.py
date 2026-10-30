import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.evidence import EvidenceError, create_evidence
from hactors_cli.core.harness_run import create_harness_run
from hactors_cli.core.plan_run import create_plan_run
from hactors_cli.core.project import create_project
from hactors_cli.core.state import load_state, set_active_run
from hactors_cli.core.test_run import create_test_run

TEMPLATE_DEFAULTS = {
    "id": "",
    "title": "",
    "kind": "",
    "relations": [],
    "source": {"rfc": "", "harness": "", "execution": "", "artifact": "", "commit": ""},
    "environment": {"platform": "", "commands": [], "outputs": []},
    "recorded": "",
}


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


def expected_evidence(evidence_id, field, origin, **overrides):
    data = {
        "id": evidence_id,
        "title": "",
        "kind": "",
        "relations": [],
        "source": {"rfc": "", "harness": "", "execution": "", "artifact": "", "commit": ""},
        "environment": {"platform": "", "commands": [], "outputs": []},
        "recorded": "",
    }
    data["source"][field] = origin
    data.update(overrides)
    return data


def test_execution_origin_records_full_path_next_to_the_run(hactors_root, harness_origin, load_yaml):
    project, ancestors = harness_origin
    harness = ancestors[-1]
    origin = harness.relative_to(project).as_posix()
    originals = {run / "manifest.yaml": (run / "manifest.yaml").read_bytes() for run in ancestors}
    state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()
    before = snapshot(hactors_root)
    expected_project = load_yaml(project / "manifest.yaml")
    expected_project["counters"]["evidence"] += 1

    path = create_evidence(hactors_root, project.name, origin)

    assert path == harness / "EVD-00001.yaml"
    assert load_yaml(path) == expected_evidence("EVD-00001", "execution", origin)
    assert load_yaml(project / "manifest.yaml") == expected_project
    assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before
    assert load_state(hactors_root)["active_run_path"] == origin
    added = path.relative_to(hactors_root).as_posix()
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {added}
    assert before.keys() - after.keys() == set()
    assert [p for p in before if before[p] != after[p]] == ["projects/proj/manifest.yaml"]
    assert all(p.read_bytes() == content for p, content in originals.items())


def test_execution_origin_works_at_any_depth_and_for_any_run_type(hactors_root, harness_origin, load_yaml):
    project, ancestors = harness_origin
    counter = 0
    for run in ancestors:
        origin = run.relative_to(project).as_posix()
        counter += 1
        path = create_evidence(hactors_root, project.name, origin)
        assert path == run / f"EVD-{counter:05d}.yaml"
        assert load_yaml(path) == expected_evidence(f"EVD-{counter:05d}", "execution", origin)
    assert load_yaml(project / "manifest.yaml")["counters"]["evidence"] == counter


@pytest.mark.parametrize("origin,directory", [
    ("rfcs/RFC-A00001.md", "rfcs"),
    ("tasks/TASK-00001.md", "tasks"),
    ("standards/GIT.md", "standards"),
    ("rfcs", "rfcs"),
    ("standards", "standards"),
    ("project.yaml", ""),
    ("manifest.yaml", ""),
])
def test_artifact_origin_is_recorded_verbatim_in_its_own_directory(
    hactors_root, artifacts, load_yaml, origin, directory,
):
    project = artifacts
    before = snapshot(project)

    path = create_evidence(hactors_root, project.name, origin)

    assert path == project / directory / "EVD-00001.yaml"
    assert load_yaml(path) == expected_evidence("EVD-00001", "artifact", origin)
    assert load_yaml(project / "manifest.yaml")["counters"]["evidence"] == 1
    after = snapshot(project)
    assert after.keys() - before.keys() == {path.relative_to(project).as_posix()}
    assert {p for p in before if before[p] != after[p]} == {"manifest.yaml"}
    assert (project / "rfcs" / "RFC-A00001.md").read_text() == "# RFC original\n"
    assert not (project / "evidence").exists()
    assert not (project / "evidences").exists()


@pytest.mark.parametrize("field,value", [
    ("title", "Resultado observado"),
    ("kind", "test-output"),
    ("recorded", "2026-10-30"),
])
def test_explicit_options_override_only_their_own_field(hactors_root, artifacts, load_yaml, field, value):
    project = artifacts
    path = create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md", **{field: value})
    assert load_yaml(path) == expected_evidence(
        "EVD-00001", "artifact", "rfcs/RFC-A00001.md", **{field: value}
    )


@pytest.mark.parametrize("kwargs", [
    {}, {"title": ""}, {"kind": ""}, {"recorded": ""},
    {"title": "", "kind": "", "recorded": ""},
    {"title": "observación", "kind": "observation", "recorded": "2026-10-30"},
])
def test_template_defaults_are_preserved_unless_a_value_is_explicit(
    hactors_root, artifacts, load_yaml, kwargs,
):
    project = artifacts
    source = hactors_root / "specs" / "templates" / "evidence_template.yaml"
    template = load_yaml(source)
    template["title"] = "título de la plantilla"
    template["kind"] = "document"
    template["recorded"] = "1999-01-01"
    template["relations"] = [{"target": "RFC-A00001#C1", "relation": "verifies"}]
    template["environment"] = {"platform": "linux", "commands": ["make check"], "outputs": ["ok"]}
    template["source"].update(rfc="RFC-PLANTILLA", harness="HRN-00001@v001", commit="deadbeef")
    source.write_text(yaml.safe_dump(template))
    original_bytes = source.read_bytes()

    path = create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md", **kwargs)

    expected = dict(template)
    expected["id"] = "EVD-00001"
    expected["source"] = dict(template["source"], artifact="rfcs/RFC-A00001.md")
    expected.update(kwargs)
    assert load_yaml(path) == expected
    assert source.read_bytes() == original_bytes

    sibling = create_evidence(hactors_root, project.name, "tasks/TASK-00001.md")
    template["id"] = "EVD-00002"
    template["source"] = dict(template["source"], artifact="tasks/TASK-00001.md")
    assert load_yaml(sibling) == template
    assert load_yaml(path) == expected


@pytest.mark.parametrize("value", [
    "kind-inventado", "ayer", "  espaciado  ", "línea: 'uno'\nsegunda # literal",
    "$(touch ejecutado); ./receta.py", "../../../fuera", "42", "null", "[]",
])
def test_declared_values_are_stored_verbatim_without_validation(hactors_root, artifacts, load_yaml, value):
    project = artifacts
    path = create_evidence(
        hactors_root, project.name, "rfcs/RFC-A00001.md", title=value, kind=value, recorded=value,
    )
    data = load_yaml(path)
    assert data["title"] == data["kind"] == data["recorded"] == value
    assert not (project / "ejecutado").exists()


def test_counter_is_project_global_across_origins(hactors_root, harness_origin, load_yaml):
    project, ancestors = harness_origin
    (project / "rfcs" / "RFC-A00001.md").write_text("# RFC\n")
    plan = create_plan_run(hactors_root, project.name, ancestors[2].relative_to(project).as_posix())
    origins = [
        "rfcs/RFC-A00001.md",
        ancestors[-1].relative_to(project).as_posix(),
        plan.relative_to(project).as_posix(),
        "rfcs",
    ]
    paths = [create_evidence(hactors_root, project.name, origin) for origin in origins]
    assert [path.name for path in paths] == [f"EVD-{i:05d}.yaml" for i in range(1, 5)]
    assert paths[0].parent == project / "rfcs"
    assert paths[1].parent == ancestors[-1]
    assert paths[2].parent == plan
    assert paths[3].parent == project / "rfcs"
    assert len({path.stat().st_ino for path in paths}) == 4
    assert load_yaml(project / "manifest.yaml")["counters"]["evidence"] == 4
    fields = ["artifact", "execution", "execution", "artifact"]
    for path, field, origin in zip(paths, fields, origins):
        assert load_yaml(path)["source"][field] == origin


def test_other_project_counters_are_untouched(hactors_root, harness_origin, load_yaml):
    project, ancestors = harness_origin
    manifest = project / "manifest.yaml"
    counters = load_yaml(manifest)["counters"].copy()
    create_evidence(hactors_root, project.name, ancestors[-1].relative_to(project).as_posix())
    counters["evidence"] = 1
    assert load_yaml(manifest)["counters"] == counters


def test_creation_never_changes_the_active_selection(hactors_root, harness_origin):
    project, ancestors = harness_origin
    for run in (ancestors[-1], ancestors[-2], ancestors[0]):
        origin = run.relative_to(project).as_posix()
        set_active_run(hactors_root, project.name, origin)
        state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()
        create_evidence(hactors_root, project.name, origin)
        assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before
        assert load_state(hactors_root)["active_run_path"] == origin


@pytest.mark.parametrize("origin", [
    "", "   ", "/tmp/fuera", "../fuera", "rfcs/../rfcs", ".", "./rfcs", "rfcs/.", "..",
    "rfcs//RFC-A00001.md", "rfcs/", "/rfcs/RFC-A00001.md", "rfcs\\RFC-A00001.md",
    "hactors", "hactors/", "missing.md", "rfcs/missing.md", "rfcs/missing/dir.md",
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
    with pytest.raises(EvidenceError):
        create_evidence(hactors_root, project.name, origin)
    assert snapshot(hactors_root) == before


def test_valid_run_origin_is_required_to_have_a_manifest(hactors_root, harness_origin):
    project, ancestors = harness_origin
    harness = ancestors[-1]
    (harness / "manifest.yaml").unlink()
    before = snapshot(hactors_root)
    with pytest.raises(EvidenceError, match="manifest"):
        create_evidence(hactors_root, project.name, harness.relative_to(project).as_posix())
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("escape", [False, True], ids=["internal", "external"])
def test_symlinked_origin_is_rejected_without_writing_target(
    hactors_root, artifacts, tmp_path, escape,
):
    project = artifacts
    original = project / "rfcs" / "RFC-A00001.md"
    target = (tmp_path if escape else project / "rfcs") / "original.md"
    original.rename(target)
    original.symlink_to(target)
    before = snapshot(tmp_path)
    with pytest.raises(EvidenceError, match="enlaces simbólicos"):
        create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert snapshot(tmp_path) == before


def test_symlinked_directory_origin_is_rejected(hactors_root, artifacts, tmp_path):
    project = artifacts
    target = tmp_path / "rfcs-reales"
    project.joinpath("rfcs").rename(target)
    project.joinpath("rfcs").symlink_to(target, target_is_directory=True)
    before = snapshot(tmp_path)
    with pytest.raises(EvidenceError, match="enlaces simbólicos"):
        create_evidence(hactors_root, project.name, "rfcs")
    assert snapshot(tmp_path) == before


def test_existing_evidence_is_never_overwritten_nor_counted(hactors_root, artifacts, load_yaml):
    project = artifacts
    existing = project / "rfcs" / "EVD-00001.yaml"
    existing.write_text("id: EVD-00001\nmanual: no sobrescribir\n")
    before = snapshot(hactors_root)
    with pytest.raises(EvidenceError, match="Ya existe"):
        create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert snapshot(hactors_root) == before
    assert load_yaml(project / "manifest.yaml")["counters"]["evidence"] == 0

    existing.unlink()
    create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert load_yaml(project / "manifest.yaml")["counters"]["evidence"] == 1


def test_existing_evidence_in_a_run_directory_is_never_overwritten(hactors_root, harness_origin):
    project, ancestors = harness_origin
    harness = ancestors[-1]
    (harness / "EVD-00001.yaml").write_text("id: EVD-00001\n")
    before = snapshot(hactors_root)
    with pytest.raises(EvidenceError, match="Ya existe"):
        create_evidence(hactors_root, project.name, harness.relative_to(project).as_posix())
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("value", [-1, True, False, 1.5, "1", None, [], {}])
def test_invalid_counter_is_rejected_before_any_write(hactors_root, artifacts, load_yaml, value):
    project = artifacts
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"]["evidence"] = value
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)
    with pytest.raises(EvidenceError, match="Contador inválido"):
        create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("value", [None, [], "inválido", 1, False])
def test_invalid_counters_mapping_is_rejected_before_any_write(hactors_root, artifacts, load_yaml, value):
    project = artifacts
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"] = value
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)
    with pytest.raises(EvidenceError, match="Contadores inválidos"):
        create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert snapshot(hactors_root) == before


def test_missing_counter_is_added_starting_at_one(hactors_root, artifacts, load_yaml):
    project = artifacts
    manifest = project / "manifest.yaml"
    data = load_yaml(manifest)
    data["counters"].pop("evidence")
    manifest.write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)

    path = create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md")

    assert path.name == "EVD-00001.yaml"
    data["counters"]["evidence"] = 1
    assert load_yaml(manifest) == data
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {path.relative_to(hactors_root).as_posix()}
    assert {p for p in before if before[p] != after[p]} == {"projects/proj/manifest.yaml"}


@pytest.mark.parametrize("source", ["missing", None, [], "inválido", 42, False])
def test_non_mapping_template_source_fails_before_writes(hactors_root, artifacts, load_yaml, source):
    project = artifacts
    template_path = hactors_root / "specs" / "templates" / "evidence_template.yaml"
    template = load_yaml(template_path)
    if source == "missing":
        template.pop("source")
    else:
        template["source"] = source
    template_path.write_text(yaml.safe_dump(template))
    before = snapshot(hactors_root)
    with pytest.raises(EvidenceError, match="source"):
        create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("problem", ["missing", "broken", "non-mapping"])
def test_template_problems_are_reported_without_writes(hactors_root, artifacts, problem):
    project = artifacts
    template_path = hactors_root / "specs" / "templates" / "evidence_template.yaml"
    if problem == "missing":
        template_path.unlink()
    elif problem == "broken":
        template_path.write_text("id: [roto\n")
    else:
        template_path.write_text("[]\n")
    before = snapshot(hactors_root)
    with pytest.raises(EvidenceError):
        create_evidence(hactors_root, project.name, "rfcs/RFC-A00001.md")
    assert snapshot(hactors_root) == before


def test_evidence_template_matches_the_normative_schema(hactors_root, load_yaml):
    assert load_yaml(hactors_root / "specs" / "templates" / "evidence_template.yaml") == TEMPLATE_DEFAULTS


def test_cli_help_documents_origin_and_declared_fields():
    runner = CliRunner()
    assert "create-evidence" in runner.invoke(cli, ["--help"]).output
    result = runner.invoke(cli, ["create-evidence", "--help"])
    assert result.exit_code == 0
    for option in ("--origin", "--title", "--kind", "--recorded", "--root"):
        assert option in result.output
    assert "instancia activa" in " ".join(result.output.split())


def test_cli_requires_active_project(hactors_root, artifacts):
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-evidence", "--origin", "rfcs/RFC-A00001.md", expected=1)
    assert "No hay proyecto activo" in result.output
    assert "use-project" in result.output
    assert snapshot(hactors_root) == before


def test_cli_without_origin_still_requires_an_active_project(hactors_root, artifacts):
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-evidence", expected=1)
    assert "No hay proyecto activo" in result.output
    assert snapshot(hactors_root) == before


@pytest.mark.parametrize("depth", [0, 1, 2, 3, 4])
def test_cli_defaults_origin_to_the_active_run_at_any_depth(hactors_root, harness_origin, load_yaml, depth):
    project, ancestors = harness_origin
    run = ancestors[depth]
    origin = run.relative_to(project).as_posix()
    invoke(hactors_root, "use-project", project.name)
    invoke(hactors_root, "use-run", origin)
    state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()

    result = invoke(hactors_root, "create-evidence")

    assert "Evidencia creada" in result.output
    assert load_yaml(run / "EVD-00001.yaml") == expected_evidence("EVD-00001", "execution", origin)
    assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before


def test_cli_without_origin_requires_an_active_run(hactors_root, artifacts):
    project = artifacts
    invoke(hactors_root, "use-project", project.name)
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-evidence", expected=1)
    assert "No hay instancia activa" in result.output
    assert snapshot(hactors_root) == before


def test_cli_empty_origin_is_invalid_even_with_an_active_run(hactors_root, harness_origin):
    project, ancestors = harness_origin
    invoke(hactors_root, "use-project", project.name)
    invoke(hactors_root, "use-run", ancestors[-1].relative_to(project).as_posix())
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-evidence", "--origin", "", expected=1)
    assert "Origen inválido" in result.output
    assert snapshot(hactors_root) == before


def test_cli_creates_evidence_from_execution_and_artifact_origins(hactors_root, harness_origin, load_yaml):
    project, ancestors = harness_origin
    harness = ancestors[-1]
    invoke(hactors_root, "use-project", project.name)
    state_before = (hactors_root / "projects" / ".state.yaml").read_bytes()

    result = invoke(hactors_root, "create-evidence", "--origin", harness.relative_to(project).as_posix())
    assert "Evidencia creada" in result.output
    assert load_yaml(harness / "EVD-00001.yaml") == expected_evidence(
        "EVD-00001", "execution", harness.relative_to(project).as_posix(),
    )

    (project / "rfcs" / "RFC-A00001.md").write_text("# RFC\n")
    invoke(
        hactors_root, "create-evidence", "--origin", "rfcs/RFC-A00001.md",
        "--title", "Salida verificada", "--kind", "test-output", "--recorded", "2026-10-30",
    )
    assert load_yaml(project / "rfcs" / "EVD-00002.yaml") == expected_evidence(
        "EVD-00002", "artifact", "rfcs/RFC-A00001.md",
        title="Salida verificada", kind="test-output", recorded="2026-10-30",
    )
    assert load_yaml(project / "manifest.yaml")["counters"]["evidence"] == 2
    assert (hactors_root / "projects" / ".state.yaml").read_bytes() == state_before


def test_cli_root_is_autodetected_from_the_working_directory(
    hactors_root, harness_origin, monkeypatch, load_yaml,
):
    project, ancestors = harness_origin
    harness = ancestors[-1]
    invoke(hactors_root, "use-project", project.name)
    monkeypatch.chdir(harness)
    origin = harness.relative_to(project).as_posix()

    result = CliRunner().invoke(cli, ["create-evidence", "--origin", origin])

    assert result.exit_code == 0, result.output
    assert load_yaml(harness / "EVD-00001.yaml") == expected_evidence("EVD-00001", "execution", origin)


@pytest.mark.parametrize("args,message", [
    (("--origin", "missing.md"), "no encontrado"),
    (("--origin", "../fuera"), "Origen inválido"),
    (("--origin", "hactors"), "Origen inválido"),
    (("--origin", ""), "Origen inválido"),
])
def test_cli_reports_invalid_origin_without_writes(hactors_root, artifacts, args, message):
    project = artifacts
    invoke(hactors_root, "use-project", project.name)
    before = snapshot(hactors_root)
    result = invoke(hactors_root, "create-evidence", *args, expected=1)
    assert message in result.output
    assert snapshot(hactors_root) == before


def test_cli_works_with_an_unrelated_active_run(hactors_root, harness_origin, load_yaml):
    project, ancestors = harness_origin
    invoke(hactors_root, "use-project", project.name)
    invoke(hactors_root, "use-run", ancestors[-1].relative_to(project).as_posix())
    (project / "rfcs" / "RFC-A00001.md").write_text("# RFC\n")

    invoke(hactors_root, "create-evidence", "--origin", "rfcs/RFC-A00001.md")

    assert load_yaml(project / "rfcs" / "EVD-00001.yaml") == expected_evidence(
        "EVD-00001", "artifact", "rfcs/RFC-A00001.md",
    )
    assert not list(ancestors[-1].glob("EVD-*.yaml"))
    assert load_state(hactors_root)["active_run_path"] == ancestors[-1].relative_to(project).as_posix()


def test_cli_process_creates_evidence_in_a_separate_process(hactors_root, artifacts, load_yaml):
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
    before = snapshot(hactors_root)
    assert "Evidencia creada" in process(
        "create-evidence", "--origin", "rfcs/RFC-A00001.md", "--kind", "document",
    )
    assert load_yaml(project / "rfcs" / "EVD-00001.yaml") == expected_evidence(
        "EVD-00001", "artifact", "rfcs/RFC-A00001.md", kind="document",
    )
    after = snapshot(hactors_root)
    assert after.keys() - before.keys() == {"projects/proj/rfcs/EVD-00001.yaml"}
    assert {p for p in before if before[p] != after[p]} == {"projects/proj/manifest.yaml"}
