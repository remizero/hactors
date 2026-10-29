from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from hactors_cli.core.harness_run import HarnessRunError, create_harness_run
from hactors_cli.core.paths import require_run_directory
from hactors_cli.core.plan_run import create_plan_run
from hactors_cli.core.rfc_run import create_rfc_run
from hactors_cli.core.state import StateError, load_state, set_active_run
from hactors_cli.core.test_run import create_test_run


def snapshot(directory):
    return {
        path.relative_to(directory).as_posix(): (
            ("link", str(path.readlink())) if path.is_symlink() else
            ("directory",) if path.is_dir() else ("file", path.read_bytes())
        )
        for path in directory.rglob("*")
    }


@pytest.fixture
def test_parent(hactors_root, rfc_parent):
    project, ancestors = rfc_parent
    test = create_test_run(hactors_root, project.name, ancestors[-1].relative_to(project).as_posix())
    return project, [*ancestors, test]


def test_creation_only_adds_directory_manifest_counter_and_selection(hactors_root, test_parent, load_yaml):
    project, ancestors = test_parent
    parent = ancestors[-1]
    # References to executable recipes and published content are declarations only.
    recipe = project / "harnesses" / "HRN-00001" / "v1" / "recipe.py"
    recipe.parent.mkdir(parents=True)
    recipe.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "Path(__file__).with_name('executed').write_text('unexpected execution')\n"
    )
    recipe.chmod(0o755)
    content = recipe.parent / "content.yaml"
    content.write_text("hash: deliberately-not-a-valid-hash\nbuild: ./recipe.py\nrun: ./recipe.py\n")
    (recipe.parent / "version.yaml").write_text("version: v1\nimmutable: true\n")
    (project / "harnesses" / "catalog.yaml").write_text("catalog: [deliberately invalid YAML")
    (project / "rfcs" / "RFC-A00001.md").write_text("Keep the RFC unchanged\n")
    (project / "tasks" / "task_000001.md").write_text("Keep the task unchanged\n")
    before = snapshot(hactors_root)
    expected_project = load_yaml(project / "manifest.yaml")
    expected_project["counters"]["harness_run"] += 1
    path = parent.relative_to(project).as_posix()
    assert require_run_directory(hactors_root, project.name, path, child_type="harness_run") == parent

    run = create_harness_run(
        hactors_root, project.name, path,
        harness_ref=recipe.relative_to(project).as_posix(), content_ref=content.relative_to(project).as_posix(),
    )

    assert run == parent / "harness_run_000001"
    assert load_yaml(run / "manifest.yaml") == {
        "identity": {
            "id": run.name, "harness_ref": recipe.relative_to(project).as_posix(),
            "content_ref": content.relative_to(project).as_posix(),
        },
        "execution": {"source_revision": "", "parameters": {}},
        "state": {"status": "", "blocked_reason": ""},
    }
    assert load_yaml(project / "manifest.yaml") == expected_project
    state = {"active_project": project.name, "active_run_path": run.relative_to(project).as_posix()}
    assert load_state(hactors_root) == load_yaml(hactors_root / "projects" / ".state.yaml") == state
    assert Path(state["active_run_path"]).parts[1:] == tuple(p.name for p in [*ancestors, run])
    assert require_run_directory(hactors_root, project.name, state["active_run_path"]) == run
    after = snapshot(hactors_root)
    added = run.relative_to(hactors_root).as_posix()
    assert after.keys() - before.keys() == {added, f"{added}/manifest.yaml"}
    assert before.keys() - after.keys() == set()
    assert {path for path in before if before[path] != after[path]} == {
        "projects/proj/manifest.yaml", "projects/.state.yaml",
    }
    assert not recipe.with_name("executed").exists()


@pytest.mark.parametrize("field", ["harness_ref", "content_ref"])
@pytest.mark.parametrize("reference", [
    "", "   ", "opaque reference", "../missing", "/nonexistent/recipe.py", "HRN-00001@v1",
    "sha256:not-a-hash", "https://invalid.example/content#version=1",
    "línea: 'uno'\nsegunda # literal\n---\n&anchor [x, y]", "$(touch executed); ./recipe.py",
])
def test_references_are_opaque_and_preserved_verbatim(hactors_root, test_parent, load_yaml, field, reference):
    project, ancestors = test_parent
    run = create_harness_run(
        hactors_root, project.name, ancestors[-1].relative_to(project).as_posix(), **{field: reference},
    )
    expected = {"id": run.name, "harness_ref": "", "content_ref": ""}
    expected[field] = reference
    assert load_yaml(run / "manifest.yaml")["identity"] == expected
    assert list(run.iterdir()) == [run / "manifest.yaml"]
    assert list((project / "rfcs").iterdir()) == []
    assert not (project / "harnesses").exists()


@pytest.mark.parametrize("harness_ref", [None, "", "explicit harness"])
@pytest.mark.parametrize("content_ref", [None, "", "explicit content"])
def test_all_defaults_preserved_unless_reference_is_explicit(
    hactors_root, test_parent, load_yaml, harness_ref, content_ref,
):
    project, ancestors = test_parent
    source = hactors_root / "specs" / "templates" / "harness_run_template.yaml"
    template = load_yaml(source)
    template["identity"].update(id="template-id", harness_ref="default HRN@v3", content_ref="default content")
    template["execution"].update(source_revision="source: revision", parameters={"retries": 3, "args": ["--dry-run"]})
    template["state"].update(status="pending", blocked_reason="manual approval")
    source.write_text(yaml.safe_dump(template))
    before = source.read_bytes()
    expected = deepcopy(template)
    kwargs = {key: value for key, value in {"harness_ref": harness_ref, "content_ref": content_ref}.items() if value is not None}
    run = create_harness_run(hactors_root, project.name, ancestors[-1].relative_to(project).as_posix(), **kwargs)
    expected["identity"].update(id=run.name, **kwargs)
    assert load_yaml(run / "manifest.yaml") == expected
    assert source.read_bytes() == before
    # Rendering a second instance must not retain the previous explicit overrides.
    sibling = create_harness_run(
        hactors_root, project.name, ancestors[-1].relative_to(project).as_posix(),
        harness_ref=None, content_ref=None,
    )
    template["identity"]["id"] = sibling.name
    assert load_yaml(sibling / "manifest.yaml") == template
    assert load_yaml(run / "manifest.yaml") == expected


@pytest.mark.parametrize("identity", ["missing", None, [], "invalid", 42, False])
def test_non_mapping_template_identity_fails_before_writes(hactors_root, test_parent, load_yaml, identity):
    project, ancestors = test_parent
    source = hactors_root / "specs" / "templates" / "harness_run_template.yaml"
    template = load_yaml(source)
    if identity == "missing":
        template.pop("identity")
    else:
        template["identity"] = identity
    source.write_text(yaml.safe_dump(template))
    before = snapshot(hactors_root)
    with pytest.raises(HarnessRunError, match="identity"):
        create_harness_run(hactors_root, project.name, ancestors[-1].relative_to(project).as_posix())
    assert snapshot(hactors_root) == before


def test_reusing_version_creates_independent_siblings_and_runs_under_other_tests(hactors_root, test_parent, load_yaml):
    project, ancestors = test_parent
    rfc, test = ancestors[-2:]
    path = test.relative_to(project).as_posix()
    version = project / "harnesses" / "HRN-00001" / "v1"
    version.mkdir(parents=True)
    (version / "recipe.yaml").write_text("steps: [do-not-run]\n")
    (version / "content.yaml").write_text("hash: not-verified\n")
    (version.parent.parent / "catalog.yaml").write_text("HRN-00001: v1\n")
    original_assets = snapshot(project / "harnesses")
    originals = {run / "manifest.yaml": (run / "manifest.yaml").read_bytes() for run in ancestors}
    counters = load_yaml(project / "manifest.yaml")["counters"].copy()
    refs = {"harness_ref": "HRN-00001@v1", "content_ref": "harnesses/HRN-00001/v1/content.yaml"}
    first = create_harness_run(hactors_root, project.name, path, **refs)
    second = create_harness_run(hactors_root, project.name, path, **refs)
    sibling_test = create_test_run(hactors_root, project.name, rfc.relative_to(project).as_posix())
    third = create_harness_run(hactors_root, project.name, sibling_test.relative_to(project).as_posix(), **refs)
    plan = create_plan_run(hactors_root, project.name, rfc.relative_to(project).as_posix())
    derived = create_rfc_run(hactors_root, project.name, plan.relative_to(project).as_posix())
    derived_test = create_test_run(hactors_root, project.name, derived.relative_to(project).as_posix())
    fourth = create_harness_run(hactors_root, project.name, derived_test.relative_to(project).as_posix(), **refs)
    runs = [first, second, third, fourth]
    assert [run.name for run in runs] == [f"harness_run_{i:06d}" for i in range(1, 5)]
    assert first.parent == second.parent == test
    assert third.parent == sibling_test and sibling_test.parent == rfc
    assert fourth.parent == derived_test and derived_test.parent == derived
    assert len({(run / "manifest.yaml").stat().st_ino for run in runs}) == 4
    for run in runs:
        assert list(run.iterdir()) == [run / "manifest.yaml"]
        assert not run.is_symlink() and not (run / "manifest.yaml").is_symlink()
        assert load_yaml(run / "manifest.yaml")["identity"] == {"id": run.name, **refs}
    counters["harness_run"] += 4
    counters["test_run"] += 2
    counters["plan_run"] += 1
    counters["rfc_run"] += 1
    assert load_yaml(project / "manifest.yaml")["counters"] == counters
    assert snapshot(project / "harnesses") == original_assets
    assert all(path.read_bytes() == content for path, content in originals.items())
    untouched = {run: (run / "manifest.yaml").read_bytes() for run in runs[1:]}
    data = load_yaml(first / "manifest.yaml")
    data["execution"]["parameters"]["local-only"] = True
    (first / "manifest.yaml").write_text(yaml.safe_dump(data))
    assert all((run / "manifest.yaml").read_bytes() == content for run, content in untouched.items())
    before = snapshot(project)
    for run in reversed(runs):
        set_active_run(hactors_root, project.name, run.relative_to(project).as_posix())
        assert load_state(hactors_root) == {
            "active_project": project.name, "active_run_path": run.relative_to(project).as_posix(),
        }
    assert snapshot(project) == before


@pytest.mark.parametrize("parent_type", ["workflow_run", "task_run", "rfc_run", "plan_run", "harness_run"])
def test_harness_parent_rules_cannot_be_bypassed_by_existing_directory(
    hactors_root, test_parent, load_yaml, parent_type,
):
    project, ancestors = test_parent
    rfc = ancestors[-2]
    plan = create_plan_run(hactors_root, project.name, rfc.relative_to(project).as_posix())
    harness = create_harness_run(hactors_root, project.name, ancestors[-1].relative_to(project).as_posix())
    parent = {
        "workflow_run": ancestors[0], "task_run": ancestors[1], "rfc_run": rfc,
        "plan_run": plan, "harness_run": harness,
    }[parent_type]
    path = parent.relative_to(project).as_posix()
    before = snapshot(hactors_root)
    with pytest.raises(ValueError, match="No se puede crear"):
        require_run_directory(hactors_root, project.name, path, child_type="harness_run")
    with pytest.raises(HarnessRunError, match="No se puede crear"):
        create_harness_run(hactors_root, project.name, path)
    assert snapshot(hactors_root) == before
    misplaced = parent / "harness_run_999999"
    misplaced.mkdir()
    data = load_yaml(harness / "manifest.yaml")
    data["identity"]["id"] = misplaced.name
    (misplaced / "manifest.yaml").write_text(yaml.safe_dump(data))
    before = snapshot(hactors_root)
    with pytest.raises(ValueError, match="Jerarquía inválida"):
        require_run_directory(hactors_root, project.name, misplaced.relative_to(project).as_posix())
    with pytest.raises(StateError, match="Jerarquía inválida"):
        set_active_run(hactors_root, project.name, misplaced.relative_to(project).as_posix())
    assert snapshot(hactors_root) == before
