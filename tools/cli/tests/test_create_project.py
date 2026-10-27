from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.project import (
    InvalidProjectNameError,
    ProjectAlreadyExistsError,
    create_project,
    validate_name,
)
from hactors_cli.core.templates import TemplateNotFoundError, load_template


# ── validate_name ──────────────────────────────────────────────────

class TestValidateName:
    def test_valid_names(self):
        for name in ("mi-proyecto", "proyecto_1", "abc", "A-B_C-1"):
            validate_name(name)

    def test_empty_name(self):
        with pytest.raises(InvalidProjectNameError, match="vacío"):
            validate_name("")

    def test_name_too_long(self):
        with pytest.raises(InvalidProjectNameError, match="excede"):
            validate_name("a" * 65)

    def test_name_with_spaces(self):
        with pytest.raises(InvalidProjectNameError, match="inválido"):
            validate_name("mi proyecto")

    def test_name_with_special_chars(self):
        with pytest.raises(InvalidProjectNameError, match="inválido"):
            validate_name("proyecto@v1")

    def test_name_with_slashes(self):
        with pytest.raises(InvalidProjectNameError, match="inválido"):
            validate_name("path/to/project")


# ── create_project (core) ──────────────────────────────────────────

class TestCreateProject:
    def test_creates_directory_structure(self, hactors_root: Path):
        target = create_project("test-project", hactors_root)

        assert target.is_dir()
        assert (target / "hactors").is_dir()
        assert (target / "rfcs").is_dir()
        assert (target / "standards").is_dir()
        assert (target / "project.yaml").is_file()
        assert (target / "manifest.yaml").is_file()

    def test_project_yaml_fields_from_template(self, hactors_root: Path, load_yaml):
        create_project("test-project", hactors_root)

        data = load_yaml(hactors_root / "projects" / "test-project" / "project.yaml")

        assert data["name"] == "test-project"
        assert data["specs_ref"] == "specs/PROJECTS.md"
        assert data["description"] == ""
        assert "created_at" in data
        assert data["created_at"]

    def test_manifest_yaml_fields_from_template(self, hactors_root: Path, load_yaml):
        create_project("test-project", hactors_root)

        data = load_yaml(hactors_root / "projects" / "test-project" / "manifest.yaml")

        assert data["project"] == "test-project"
        assert data["relations"] == []

    def test_created_at_is_valid_iso8601(self, hactors_root: Path, load_yaml):
        create_project("test-project", hactors_root)

        data = load_yaml(hactors_root / "projects" / "test-project" / "project.yaml")
        parsed = datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        assert parsed.tzinfo is None

    def test_yaml_fields_match_template_keys(self, hactors_root: Path, load_yaml):
        template_path = hactors_root / "specs" / "templates" / "project_template.yaml"
        with template_path.open() as f:
            template = yaml.safe_load(f)

        create_project("test-project", hactors_root)
        data = load_yaml(hactors_root / "projects" / "test-project" / "project.yaml")

        for key in template:
            assert key in data, f"Campo '{key}' de la plantilla falta en project.yaml generado"

    def test_manifest_fields_match_template_keys(self, hactors_root: Path, load_yaml):
        template_path = hactors_root / "specs" / "templates" / "manifest_template.yaml"
        with template_path.open() as f:
            template = yaml.safe_load(f)

        create_project("test-project", hactors_root)
        data = load_yaml(hactors_root / "projects" / "test-project" / "manifest.yaml")

        for key in template:
            assert key in data, f"Campo '{key}' de la plantilla falta en manifest.yaml generado"

    def test_description_is_set(self, hactors_root: Path, load_yaml):
        create_project("test-project", hactors_root, description="Proyecto de prueba")

        data = load_yaml(hactors_root / "projects" / "test-project" / "project.yaml")
        assert data["description"] == "Proyecto de prueba"

    def test_already_exists_error(self, hactors_root: Path):
        create_project("test-project", hactors_root)

        with pytest.raises(ProjectAlreadyExistsError, match="Ya existe"):
            create_project("test-project", hactors_root)

    def test_already_exists_does_not_modify(self, hactors_root: Path, load_yaml):
        create_project("test-project", hactors_root)
        original = load_yaml(hactors_root / "projects" / "test-project" / "project.yaml")

        with pytest.raises(ProjectAlreadyExistsError):
            create_project("test-project", hactors_root)

        after = load_yaml(hactors_root / "projects" / "test-project" / "project.yaml")
        assert original == after

    def test_invalid_name_not_created(self, hactors_root: Path):
        with pytest.raises(InvalidProjectNameError):
            create_project("invalid name!", hactors_root)

        assert not (hactors_root / "projects" / "invalid name!").exists()

    def test_missing_template_error(self, tmp_path: Path):
        bare_root = tmp_path / "bare"
        (bare_root / "projects").mkdir(parents=True)
        (bare_root / "specs" / "templates").mkdir(parents=True)

        with pytest.raises(TemplateNotFoundError):
            create_project("test-project", bare_root)


# ── CLI (Click integration) ───────────────────────────────────────

class TestCli:
    def test_create_project_success(self, hactors_root: Path):
        runner = CliRunner()
        result = runner.invoke(cli, ["create-project", "my-project", "--root", str(hactors_root)])

        assert result.exit_code == 0
        assert "Proyecto creado" in result.output
        assert (hactors_root / "projects" / "my-project" / "project.yaml").is_file()

    def test_create_project_duplicate(self, hactors_root: Path):
        runner = CliRunner()
        runner.invoke(cli, ["create-project", "dup", "--root", str(hactors_root)])
        result = runner.invoke(cli, ["create-project", "dup", "--root", str(hactors_root)])

        assert result.exit_code != 0
        assert "Ya existe" in result.output

    def test_create_project_invalid_name(self, hactors_root: Path):
        runner = CliRunner()
        result = runner.invoke(cli, ["create-project", "bad name!", "--root", str(hactors_root)])

        assert result.exit_code != 0

    def test_create_project_with_description(self, hactors_root: Path, load_yaml):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "create-project", "desc-project",
            "-d", "Mi descripción",
            "--root", str(hactors_root),
        ])

        assert result.exit_code == 0
        data = load_yaml(hactors_root / "projects" / "desc-project" / "project.yaml")
        assert data["description"] == "Mi descripción"

    def test_help_shows_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "create-project" in result.output
