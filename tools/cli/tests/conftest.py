import shutil
from pathlib import Path

import pytest
import yaml

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


@pytest.fixture
def hactors_root(tmp_path: Path) -> Path:
    src = FIXTURES_ROOT / "hactors_repo"
    dst = tmp_path / "hactors_repo"
    shutil.copytree(src, dst)
    return dst


@pytest.fixture
def load_yaml():
    def _load(path: Path) -> dict:
        with path.open() as f:
            return yaml.safe_load(f)
    return _load
