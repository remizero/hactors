from pathlib import Path, PurePosixPath

import yaml

from .paths import require_project_directory, require_run_directory

STATE_FILE = "projects/.state.yaml"


class StateError(Exception):
    pass


class NoActiveProjectError(StateError):
    pass


class NoActiveRunError(StateError):
    pass


def _state_path(hactors_root: Path) -> Path:
    return hactors_root / STATE_FILE


def load_state(hactors_root: Path) -> dict:
    path = _state_path(hactors_root)
    data = {}
    if path.is_file():
        try:
            data = yaml.safe_load(path.read_text())
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise StateError(
                "No se pudo leer el estado activo. "
                "Reseleccione el proyecto con 'hactors use-project <nombre>'."
            ) from exc
    if not isinstance(data, dict):
        raise StateError(
            "Estado activo inválido. "
            "Reseleccione el proyecto con 'hactors use-project <nombre>'."
        )
    if any(key in data for key in ("current_workflow_run", "current_task_run", "current_rfc_run")):
        raise StateError(
            "Formato de estado anterior. Ejecute 'hactors use-project <nombre>' "
            "y después 'hactors use-run <ruta>' para seleccionar la instancia."
        )
    state = {
        "active_project": data.get("active_project", ""),
        "active_run_path": data.get("active_run_path", ""),
    }
    if not all(isinstance(value, str) for value in state.values()):
        raise StateError("Estado activo inválido: el proyecto y la ruta deben ser cadenas.")
    if state["active_run_path"] and not state["active_project"]:
        raise StateError("Estado activo inválido: hay una ruta sin proyecto activo.")
    return state


def save_state(hactors_root: Path, state: dict) -> None:
    try:
        _state_path(hactors_root).write_text(
            yaml.dump(state, default_flow_style=False, allow_unicode=True, sort_keys=False)
        )
    except OSError as exc:
        raise StateError(f"No se pudo guardar el estado activo: {exc}") from exc


def set_active_project(hactors_root: Path, name: str) -> None:
    set_active_run(hactors_root, name, "")


def set_active_run(hactors_root: Path, project_name: str, run_path: str) -> None:
    try:
        if run_path == "":
            require_project_directory(hactors_root, project_name)
        else:
            require_run_directory(hactors_root, project_name, run_path)
    except (ValueError, OSError) as exc:
        raise StateError(str(exc)) from exc
    save_state(hactors_root, {"active_project": project_name, "active_run_path": run_path})


def require_active_project(hactors_root: Path) -> str:
    name = load_state(hactors_root)["active_project"]
    if not name:
        raise NoActiveProjectError(
            "No hay proyecto activo. Ejecute 'hactors use-project <nombre>' primero."
        )
    try:
        require_project_directory(hactors_root, name)
    except (ValueError, OSError) as exc:
        raise StateError(str(exc)) from exc
    return name


def require_active_run_path(hactors_root: Path) -> str:
    state = load_state(hactors_root)
    if not state["active_project"]:
        raise NoActiveProjectError(
            "No hay proyecto activo. Ejecute 'hactors use-project <nombre>' primero."
        )
    run_path = state["active_run_path"]
    if not run_path:
        raise NoActiveRunError(
            "No hay instancia activa. Cree un workflow con 'hactors create-workflow' "
            "o seleccione una instancia con 'hactors use-run <ruta>'."
        )
    try:
        require_run_directory(hactors_root, state["active_project"], run_path)
    except (ValueError, OSError) as exc:
        raise StateError(str(exc)) from exc
    return run_path


def select_parent_run(hactors_root: Path) -> str:
    run_path = require_active_run_path(hactors_root)
    parent = PurePosixPath(run_path).parent.as_posix()
    if parent == "hactors":
        parent = ""
    set_active_run(hactors_root, require_active_project(hactors_root), parent)
    return parent
