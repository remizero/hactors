import shutil
from pathlib import Path

import pytest
import yaml

from hactors_cli.core.plan_run import create_plan_run
from hactors_cli.core.project import create_project
from hactors_cli.core.rfc_run import create_rfc_run
from hactors_cli.core.task_run import create_task_run
from hactors_cli.core.workflow import create_workflow

TEMPLATES = Path(__file__).resolve().parents[3] / "specs" / "templates"


@pytest.fixture
def hactors_root(tmp_path: Path) -> Path:
    dst = tmp_path / "hactors_repo"
    (dst / "specs").mkdir(parents=True)
    (dst / "projects").mkdir()
    shutil.copytree(TEMPLATES, dst / "specs" / "templates")
    return dst


@pytest.fixture
def zero_counters() -> dict:
    """Los contadores que la plantilla normativa declara en un manifest nuevo."""
    with (TEMPLATES / "manifest_template.yaml").open() as f:
        return yaml.safe_load(f)["counters"]


@pytest.fixture(params=[0, 4], ids=["initial-rfc", "deep-derived-rfc"])
def rfc_parent(hactors_root, request):
    project = create_project("proj", hactors_root)
    runs = [create_workflow(hactors_root, project.name)]
    creators = [create_task_run, create_rfc_run]
    creators += [create_plan_run, create_rfc_run] * request.param
    for create in creators:
        runs.append(create(hactors_root, project.name, runs[-1].relative_to(project).as_posix()))
    return project, runs


@pytest.fixture
def load_yaml():
    def _load(path: Path) -> dict:
        with path.open() as f:
            return yaml.safe_load(f)
    return _load
