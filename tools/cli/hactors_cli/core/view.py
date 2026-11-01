import html
from pathlib import Path
from urllib.parse import quote

from .model import MODEL_SCHEMA, generated_at, root_models
from .paths import PROJECTS_DIRNAME, VIEWS_DIRNAME
from .state import StateError, load_state

VIEW_FILENAME = "index.html"
NO_STATUS = "(sin declarar)"
NO_ACTOR = "(sin actor declarado)"
KINDS = ("task", "rfc", "plan", "adr", "summary", "evidence", "finding", "harness")
STYLE = """
body { font-family: system-ui, sans-serif; margin: 0 auto; max-width: 72rem;
       padding: 2rem 1.5rem; line-height: 1.5; }
h1 { font-size: 1.6rem; margin-bottom: .2rem; }
h2 { font-size: 1.05rem; margin-top: 2rem; padding-bottom: .2rem;
     border-bottom: 1px solid rgba(127, 127, 127, .4); }
p.meta { font-size: .85rem; opacity: .75; }
table { border-collapse: collapse; width: 100%; font-size: .9rem; }
th, td { text-align: left; padding: .3rem .5rem; vertical-align: top;
         border-bottom: 1px solid rgba(127, 127, 127, .25); }
code, .kind { font-family: ui-monospace, monospace; font-size: .85em; opacity: .8; }
ul.tree { list-style: none; margin: 0; padding-left: 1.3rem; }
ol.problems { font-size: .9rem; }
.empty { opacity: .6; font-style: italic; }
.flag { font-size: .8rem; font-weight: 600; }
dl.groups { font-size: .9rem; }
dl.groups dt { font-weight: 600; margin-top: .6rem; }
dl.groups dd { margin: 0 0 0 1rem; }
"""


class ViewError(Exception):
    pass


def render_views(root: Path) -> list[Path]:
    projects = root / PROJECTS_DIRNAME
    if projects.is_symlink() or not projects.is_dir():
        raise ViewError(f"No hay un directorio '{PROJECTS_DIRNAME}/' en '{root}'.")
    try:
        entries = root_models(root)
        active = _active_project(root)
        stamp = generated_at()
        written = []
        for entry in entries:
            if entry["error"]:
                continue
            model = dict(entry["model"], generated_at=stamp)
            written.append(
                _write(
                    projects / entry["name"] / VIEWS_DIRNAME / VIEW_FILENAME,
                    render_board(model, active),
                )
            )
        written.append(
            _write(projects / VIEWS_DIRNAME / VIEW_FILENAME, render_viewer(entries, active, stamp))
        )
    except OSError as exc:
        raise ViewError(f"No se pudo escribir la vista: {exc}") from exc
    return written


def render_board(model: dict, active: str = "") -> str:
    name = model.get("project", "")
    artifacts = model.get("artifacts", [])
    runs = model.get("runs", [])
    edges = model.get("edges", [])
    problems = model.get("problems", [])
    paths = {}
    for item in artifacts:
        identity = item.get("id", "")
        if identity and identity not in paths:
            paths[identity] = item.get("path", "")
    body = [f"<h1>{_e(name)}{_flag(bool(name) and name == active)}</h1>"]
    if model.get("description"):
        body.append(f"<p>{_e(model['description'])}</p>")
    body.append(
        f"<p class='meta'>Modelo <code>{_e(MODEL_SCHEMA)}</code> proyectado el "
        f"{_e(model.get('generated_at', ''))}. Vista derivada de los artefactos: no es fuente de "
        "verdad y la CLI no la lee. Regenerar con <code>hactors render</code>.</p>"
    )
    body.append(_counters(model.get("counters", {})))
    body.append(_artifacts(artifacts))
    body.append(_actions(artifacts))
    body.append(_versions(artifacts))
    rows = _rows(artifacts)
    body.append(_by_status(rows))
    body.append(_by_actor(rows))
    body.append(_runs(runs))
    body.append(_edges(edges, paths))
    body.append(_problems(problems))
    return _page(f"{name} — tablero", body)


def render_viewer(entries: list[dict], active: str = "", stamp: str = "") -> str:
    rows = []
    for entry in entries:
        name = entry["name"]
        model = entry["model"]
        if entry["error"]:
            rows.append([
                _e(name),
                f"<span class='empty'>no proyectable: {_e(entry['error'])}</span>",
                "", "", "",
            ])
            continue
        rows.append([
            f"<a href='../{_e(quote(name))}/{VIEWS_DIRNAME}/{VIEW_FILENAME}'>{_e(name)}</a>"
            f"{_flag(name == active)}",
            _e(model.get("description", "")),
            _e(_counts(model)),
            str(len(model.get("runs", []))),
            str(len(model.get("problems", []))),
        ])
    body = [
        "<h1>Proyectos HACTORS</h1>",
        f"<p class='meta'>Visor proyectado el {_e(stamp)}. Derivado de los artefactos de cada "
        "proyecto: no es fuente de verdad y la CLI no lo lee. Regenerar con "
        "<code>hactors render</code>.</p>",
        _table(
            ["Proyecto", "Descripción", "Artefactos", "Ejecuciones", "Inconsistencias"],
            rows,
            empty="No hay ningún proyecto en la raíz.",
        ),
    ]
    return _page("Proyectos HACTORS — visor", body)


def _active_project(root: Path) -> str:
    try:
        return load_state(root)["active_project"]
    except StateError:
        return ""


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _flag(condition: bool) -> str:
    return " <span class='flag'>(proyecto activo)</span>" if condition else ""


def _page(title: str, body: list[str]) -> str:
    return (
        "<!DOCTYPE html>\n"
        "<html lang='es'>\n<head>\n<meta charset='utf-8'>\n"
        f"<title>{_e(title)}</title>\n<style>{STYLE}</style>\n</head>\n<body>\n"
        + "\n".join(part for part in body if part)
        + "\n</body>\n</html>\n"
    )


def _table(headers: list[str], rows: list[list[str]], empty: str) -> str:
    if not rows:
        return f"<p class='empty'>{_e(empty)}</p>"
    head = "".join(f"<th>{header}</th>" for header in headers)
    body = "\n".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"<table>\n<thead><tr>{head}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table>"


def _section(title: str, content: str) -> str:
    return f"<h2>{_e(title)}</h2>\n{content}"


def _link(path: str, label: str) -> str:
    if not path:
        return _e(label)
    return f"<a href='../{_e(quote(path))}'>{_e(label)}</a>"


def _counters(counters: dict) -> str:
    rows = [[f"<code>{_e(name)}</code>", _e(value)] for name, value in counters.items()]
    return _section("Contadores", _table(["Contador", "Valor"], rows, "El manifest no declara contadores."))


def _artifacts(artifacts: list[dict]) -> str:
    rows = [
        [
            _link(item.get("path", ""), item.get("id", "") or item.get("path", "")),
            f"<span class='kind'>{_e(item.get('kind', ''))}</span>",
            _e(item.get("title", "")),
            _e(item.get("status", "") or NO_STATUS),
            _e(item.get("actor", "") or NO_ACTOR),
        ]
        for item in artifacts
    ]
    return _section(
        "Artefactos",
        _table(["Identificador", "Familia", "Título", "Estado", "Actor"], rows,
               "El proyecto no tiene artefactos."),
    )


def _actions(artifacts: list[dict]) -> str:
    rows = []
    for item in artifacts:
        for action in item.get("actions", []):
            rows.append([
                _e(action.get("id", "")),
                f"<span class='kind'>{_e(action.get('type', '') or NO_STATUS)}</span>",
                _e(action.get("status", "") or NO_STATUS),
                _e(action.get("actor", "") or NO_ACTOR),
                _link(item.get("path", ""), item.get("id", "")),
            ])
    if not rows:
        return ""
    return _section(
        "Acciones derivadas",
        _table(["Acción", "Tipo", "Estado", "Actor", "RFC"], rows, ""),
    )


def _versions(artifacts: list[dict]) -> str:
    rows = []
    for item in artifacts:
        for version in item.get("versions", []):
            rows.append([
                _link(item.get("path", ""), item.get("id", "")),
                _e(version.get("version", "")),
                _e(version.get("status", "") or NO_STATUS),
                _e(version.get("published", "") or "no publicada"),
            ])
    if not rows:
        return ""
    return _section(
        "Versiones de HARNESS",
        _table(["HRN", "Versión", "Estado", "Publicada"], rows, ""),
    )


def _rows(artifacts: list[dict]) -> list[dict]:
    rows = []
    for item in artifacts:
        rows.append({
            "id": item.get("id", ""),
            "path": item.get("path", ""),
            "kind": item.get("kind", ""),
            "status": item.get("status", ""),
            "actor": item.get("actor", ""),
        })
        for action in item.get("actions", []):
            rows.append({
                "id": action.get("id", ""),
                "path": item.get("path", ""),
                "kind": "action",
                "status": action.get("status", ""),
                "actor": action.get("actor", ""),
            })
    return rows


def _by_status(rows: list[dict]) -> str:
    return _section("Por estado", _groups(_grouped(rows, "status", NO_STATUS)))


def _by_actor(rows: list[dict]) -> str:
    return _section("Por actor", _groups(_grouped(rows, "actor", NO_ACTOR)))


def _grouped(rows: list[dict], field: str, fallback: str) -> list[tuple[str, list[dict]]]:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row.get(field) or fallback, []).append(row)
    return sorted(groups.items(), key=lambda item: (item[0] == fallback, item[0]))


def _groups(groups: list[tuple[str, list[dict]]]) -> str:
    if not groups:
        return "<p class='empty'>El proyecto no tiene artefactos.</p>"
    items = []
    for key, rows in groups:
        listed = ", ".join(_link(row["path"], row["id"] or row["path"]) for row in rows)
        items.append(f"<dt>{_e(key)}</dt>\n<dd>{listed}</dd>")
    return f"<dl class='groups'>\n" + "\n".join(items) + "\n</dl>"


def _runs(runs: list[dict]) -> str:
    if not runs:
        return _section(
            "Ejecución", "<p class='empty'>El proyecto no tiene instancias de ejecución.</p>"
        )
    children: dict[str, list[dict]] = {}
    for run in runs:
        children.setdefault(run.get("parent", ""), []).append(run)
    return _section("Ejecución", _branch(children, ""))


def _branch(children: dict[str, list[dict]], parent: str) -> str:
    items = []
    for run in children.get(parent, []):
        details = [f"<span class='kind'>{_e(run.get('kind', ''))}</span>"]
        if run.get("status"):
            details.append(f"estado {_e(run['status'])}")
        if run.get("reference"):
            details.append(f"ejecuta {_e(run['reference'])}")
        if run.get("blocked_reason"):
            details.append(f"<strong>bloqueado: {_e(run['blocked_reason'])}</strong>")
        nested = _branch(children, run.get("id", ""))
        items.append(
            "<li>" + _link(run.get("path", ""), run.get("id", "")) + " — " + " · ".join(details)
            + (nested if nested else "") + "</li>"
        )
    if not items:
        return ""
    return "<ul class='tree'>\n" + "\n".join(items) + "\n</ul>"


def _edges(edges: list[dict], paths: dict[str, str]) -> str:
    rows = [
        [
            _link(paths.get(edge.get("source", ""), ""), edge.get("source", "") or NO_STATUS),
            f"<span class='kind'>{_e(edge.get('relation', ''))}</span>",
            _link(paths.get(edge.get("target", ""), ""), edge.get("target", "") or NO_STATUS),
        ]
        for edge in edges
    ]
    return _section(
        "Grafo del proyecto",
        _table(["Origen", "Relación", "Destino"], rows,
               "El manifest no registra ninguna arista."),
    )


def _problems(problems: list[str]) -> str:
    if not problems:
        return _section("Inconsistencias", "<p class='empty'>Ninguna.</p>")
    listed = "\n".join(f"<li>{_e(problem)}</li>" for problem in problems)
    return _section("Inconsistencias", f"<ol class='problems'>\n{listed}\n</ol>")


def _counts(model: dict) -> str:
    counts: dict[str, int] = {}
    for item in model.get("artifacts", []):
        counts[item.get("kind", "")] = counts.get(item.get("kind", ""), 0) + 1
    return " · ".join(f"{counts[kind]} {kind}" for kind in KINDS if counts.get(kind))
