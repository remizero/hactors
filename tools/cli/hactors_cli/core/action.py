import re

from .documents import DocumentError, yaml_blocks

ACTION_ID_PATTERN = re.compile(r"AC-[0-9]{5,}")
EVIDENCE_ID_PATTERN = re.compile(r"EVD-[0-9]{5,}")
ACTION_TYPES = frozenset(
    {"analysis", "plan", "decision", "implementation", "test", "evidence", "documentation"}
)
ACTION_STATUSES = frozenset(
    {"pending", "blocked", "in-progress", "completed", "cancelled", "superseded"}
)
ACTOR_LABELS = frozenset({"human", "agent", "ci"})
ACTOR_PROHIBITION = "..."
ACTION_FIELDS = frozenset(
    {"id", "type", "status", "actor", "depends_on", "deliverable", "evidence"}
)
UNRESOLVED = (None, "")


class ActionSchemaError(Exception):
    pass


def _actor_error(value) -> str:
    if not isinstance(value, str):
        return f"`actor` debe ser una etiqueta, no {type(value).__name__}"
    parts = [part.strip() for part in value.split("|")]
    if parts == [ACTOR_PROHIBITION]:
        return ""
    if ACTOR_PROHIBITION in parts:
        return f"`actor` no admite combinar '{ACTOR_PROHIBITION}' con otras etiquetas"
    unknown = [part for part in parts if part not in ACTOR_LABELS]
    if unknown:
        return f"`actor` contiene etiquetas fuera de DEFINITIONS.md: {', '.join(repr(u) for u in unknown)}"
    if len(set(parts)) != len(parts):
        return f"`actor` repite etiquetas: {value!r}"
    return ""


def _reference_list_error(value, pattern: re.Pattern, field: str) -> str:
    if not isinstance(value, list):
        return f"`{field}` debe ser una lista, no {type(value).__name__}"
    for entry in value:
        if not isinstance(entry, str) or not pattern.fullmatch(entry):
            return f"`{field}` contiene una referencia inválida: {entry!r}"
    return ""


def extract_actions(text: str):
    try:
        blocks = yaml_blocks(text)
    except DocumentError as exc:
        raise ActionSchemaError(str(exc)) from exc
    declared = [block["actions"] for block in blocks if isinstance(block, dict) and "actions" in block]
    if not declared:
        raise ActionSchemaError("Ningún bloque `yaml` del documento declara el campo `actions:`.")
    if len(declared) > 1:
        raise ActionSchemaError("Varios bloques `yaml` declaran `actions:`; el documento es ambiguo.")
    return declared[0]


def validate_actions(actions) -> list[str]:
    if not isinstance(actions, list):
        raise ActionSchemaError(f"`actions:` debe ser una lista, no {type(actions).__name__}.")
    findings: list[str] = []
    declared: dict[str, str] = {}
    for position, action in enumerate(actions, start=1):
        where = f"actions[{position}]"
        if not isinstance(action, dict):
            findings.append(f"{where}: debe ser un mapeo, no {type(action).__name__}.")
            continue

        action_id = action.get("id")
        if action_id in UNRESOLVED:
            findings.append(f"{where}: falta el identificador `id`.")
        elif not isinstance(action_id, str) or not ACTION_ID_PATTERN.fullmatch(action_id):
            findings.append(f"{where}: identificador inválido: {action_id!r}.")
        else:
            if action_id in declared:
                findings.append(f"{action_id}: identificador repetido; ya aparece en {declared[action_id]}.")
            else:
                declared[action_id] = where
            where = action_id

        for field in sorted(set(action) - ACTION_FIELDS):
            findings.append(f"{where}: campo ajeno al esquema: '{field}'.")

        for field, domain in (("type", ACTION_TYPES), ("status", ACTION_STATUSES)):
            value = action.get(field)
            if value in UNRESOLVED:
                continue
            if not isinstance(value, str) or value not in domain:
                findings.append(f"{where}: `{field}` fuera de dominio: {value!r}.")

        actor = action.get("actor")
        if actor not in UNRESOLVED:
            error = _actor_error(actor)
            if error:
                findings.append(f"{where}: {error}.")

        deliverable = action.get("deliverable")
        if deliverable not in UNRESOLVED and not isinstance(deliverable, str):
            findings.append(f"{where}: `deliverable` debe ser una ruta o descripción textual.")

        for field, pattern in (("depends_on", ACTION_ID_PATTERN), ("evidence", EVIDENCE_ID_PATTERN)):
            value = action.get(field)
            if value in UNRESOLVED:
                continue
            error = _reference_list_error(value, pattern, field)
            if error:
                findings.append(f"{where}: {error}.")
    return findings


def validate_rfc_actions(text: str) -> list[str]:
    return validate_actions(extract_actions(text))
