from pathlib import Path

import yaml

STATE_FILE = "projects/.state.yaml"


class StateError(Exception):
    pass


class NoActiveProjectError(StateError):
    pass


class NoActiveWorkflowRunError(StateError):
    pass


class NoActiveTaskRunError(StateError):
    pass


class NoActiveRfcRunError(StateError):
    pass


def _state_path(hactors_root: Path) -> Path:
    return hactors_root / STATE_FILE


def load_state(hactors_root: Path) -> dict:
    path = _state_path(hactors_root)
    data = {}
    if path.is_file():
        with path.open() as f:
            data = yaml.safe_load(f)
    if not isinstance(data, dict):
        data = {}
    return {
        "active_project": data.get("active_project", ""),
        "current_workflow_run": data.get("current_workflow_run", ""),
        "current_task_run": data.get("current_task_run", ""),
        "current_rfc_run": data.get("current_rfc_run", ""),
    }


def save_state(hactors_root: Path, state: dict) -> None:
    path = _state_path(hactors_root)
    path.write_text(yaml.dump(state, default_flow_style=False, allow_unicode=True, sort_keys=False))


def set_active_project(hactors_root: Path, name: str) -> None:
    state = load_state(hactors_root)
    state["active_project"] = name
    state["current_workflow_run"] = ""
    state["current_task_run"] = ""
    state["current_rfc_run"] = ""
    save_state(hactors_root, state)


def set_current_workflow_run(hactors_root: Path, run_id: str) -> None:
    state = load_state(hactors_root)
    state["current_workflow_run"] = run_id
    state["current_task_run"] = ""
    state["current_rfc_run"] = ""
    save_state(hactors_root, state)


def set_current_task_run(hactors_root: Path, run_id: str) -> None:
    state = load_state(hactors_root)
    state["current_task_run"] = run_id
    state["current_rfc_run"] = ""
    save_state(hactors_root, state)


def set_current_rfc_run(hactors_root: Path, run_id: str) -> None:
    state = load_state(hactors_root)
    state["current_rfc_run"] = run_id
    save_state(hactors_root, state)


def require_active_project(hactors_root: Path) -> str:
    state = load_state(hactors_root)
    name = state["active_project"]
    if not name:
        raise NoActiveProjectError(
            "No hay proyecto activo. Ejecute 'hactors use-project <nombre>' primero."
        )
    return name


def require_active_workflow_run(hactors_root: Path) -> str:
    state = load_state(hactors_root)
    run_id = state["current_workflow_run"]
    if not run_id:
        raise NoActiveWorkflowRunError(
            "No hay workflow_run activo. Ejecute 'hactors create-workflow' primero."
        )
    return run_id


def require_active_task_run(hactors_root: Path) -> str:
    state = load_state(hactors_root)
    run_id = state["current_task_run"]
    if not run_id:
        raise NoActiveTaskRunError(
            "No hay task_run activo. Ejecute 'hactors create-task-run' primero."
        )
    return run_id


def require_active_rfc_run(hactors_root: Path) -> str:
    state = load_state(hactors_root)
    run_id = state["current_rfc_run"]
    if not run_id:
        raise NoActiveRfcRunError(
            "No hay rfc_run activo. Ejecute 'hactors create-rfc-run' primero."
        )
    return run_id
