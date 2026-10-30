from pathlib import Path

import yaml


class TemplateNotFoundError(FileNotFoundError):
    pass


def _templates_dir(hactors_root: Path) -> Path:
    return hactors_root / "specs" / "templates"


def load_template(hactors_root: Path, template_name: str) -> dict:
    path = _templates_dir(hactors_root) / template_name
    if not path.is_file():
        raise TemplateNotFoundError(f"Plantilla no encontrada: {path}")
    with path.open() as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"La plantilla no es un diccionario YAML válido: {path}")
    return data


def render_yaml(data: dict) -> str:
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)


def render_frontmatter(data: dict, reference: str) -> str:
    return f"---\n{render_yaml(data)}---\n\n{reference}\n"


def render_project_yaml(template: dict, name: str, created_at: str, description: str = "") -> str:
    data = dict(template)
    data["name"] = name
    data["created_at"] = created_at
    data["description"] = description
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)


def render_manifest_yaml(template: dict, name: str) -> str:
    data = dict(template)
    data["project"] = name
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)


def render_run_yaml(
    template: dict, id_value: str, ref_value: str = "", ref_field: str = "", wrapper_key: str = ""
) -> str:
    data = dict(template)
    if "identity" in data and isinstance(data["identity"], dict):
        data["identity"] = dict(data["identity"])
        data["identity"]["id"] = id_value
        if ref_field:
            data["identity"][ref_field] = ref_value
    if wrapper_key:
        data = {wrapper_key: data}
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
