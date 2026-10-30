import re
from pathlib import Path
from typing import Optional

import yaml

from .counters import next_task_id
from .paths import require_project_directory
from .templates import load_template, render_frontmatter

TASK_TEMPLATE = "task_template.yaml"
TASKS_DIRNAME = "tasks"
TASK_ID_PATTERN = re.compile(r"TASK-[0-9]{5,}")
TASK_REFERENCE = "Estructura y campos: `specs/templates/TASK_TEMPLATE.md`."


class TaskError(Exception):
    pass


def render_task(data: dict) -> str:
    return render_frontmatter(data, TASK_REFERENCE)


def normalize_task_ref(task_ref: str) -> str:
    if task_ref == "":
        return ""
    if TASK_ID_PATTERN.fullmatch(task_ref):
        return task_ref
    if task_ref.startswith(f"{TASKS_DIRNAME}/"):
        filename = task_ref[len(TASKS_DIRNAME) + 1 :]
        if filename.endswith(".md") and TASK_ID_PATTERN.fullmatch(filename[:-3]):
            return filename[:-3]
    raise ValueError(
        f"Referencia de TASK inválida: '{task_ref}'. "
        "Use el identificador 'TASK-00001' o su ruta 'tasks/TASK-00001.md'."
    )


def create_task(
    root: Path,
    project_name: str,
    task: Optional[str] = None,
    actor: Optional[str] = None,
) -> tuple[str, Path]:
    try:
        project = require_project_directory(root, project_name)
        directory = project / TASKS_DIRNAME
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"El directorio '{TASKS_DIRNAME}/' del proyecto no existe.")
        template = load_template(root, TASK_TEMPLATE)
        data = dict(template)
        for field, value in (("task", task), ("actor", actor)):
            if value is not None:
                data[field] = value
        task_id, _ = next_task_id(project / "manifest.yaml", directory)
        path = directory / f"{task_id}.md"
        path.write_text(render_task(data))
    except FileExistsError as exc:
        raise TaskError(f"Ya existe una TASK en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise TaskError(str(exc)) from exc
    return task_id, path
