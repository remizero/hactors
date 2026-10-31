from pathlib import Path

import pytest
import yaml

from hactors_cli.core.action import (
    ACTION_FIELDS,
    ACTION_STATUSES,
    ACTION_TYPES,
    ACTOR_LABELS,
    ACTOR_PROHIBITION,
    ActionSchemaError,
    extract_actions,
    validate_actions,
    validate_rfc_actions,
)

SPECS_TEMPLATES = Path(__file__).resolve().parents[3] / "specs" / "templates"
SPECS = SPECS_TEMPLATES.parent

VALID = {
    "id": "AC-00001",
    "type": "implementation",
    "status": "in-progress",
    "actor": "human | agent",
    "depends_on": ["AC-00002"],
    "deliverable": "init/src/actor.cpp",
    "evidence": ["EVD-00007"],
}


def document(actions) -> str:
    body = yaml.dump({"context": "", "actions": actions}, sort_keys=False, allow_unicode=True)
    return f"# RFC-A00001\n\n```yaml\nrfc: \"RFC-A00001\"\nstatus: draft\n```\n\n```yaml\n{body}```\n"


def table_first_column(filename: Path, section: str) -> set[str]:
    text = filename.read_text()
    body = text.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
    return {line.split("|")[1].strip().strip("`") for line in body.splitlines() if line.startswith("| `")}


def test_types_match_ac_template():
    assert table_first_column(SPECS_TEMPLATES / "AC_TEMPLATE.md", "Tipos") == set(ACTION_TYPES)


def test_statuses_match_ac_template():
    assert table_first_column(SPECS_TEMPLATES / "AC_TEMPLATE.md", "Estados") == set(ACTION_STATUSES)


def test_fields_match_rfc_template():
    assert table_first_column(SPECS_TEMPLATES / "RFC_TEMPLATE.md", "Acciones derivadas") == set(ACTION_FIELDS)


def test_actor_labels_match_definitions():
    text = (SPECS / "DEFINITIONS.md").read_text()
    for label in [*ACTOR_LABELS, ACTOR_PROHIBITION]:
        assert f"[actor: {label}]" in text


@pytest.mark.parametrize(
    "action",
    [
        VALID,
        {"id": "AC-00001"},
        {
            "id": "AC-00001", "type": "", "status": "", "actor": "",
            "depends_on": [], "deliverable": "", "evidence": [],
        },
        {**VALID, "actor": "human"},
        {**VALID, "actor": "ci"},
        {**VALID, "actor": ACTOR_PROHIBITION},
        {**VALID, "actor": "human|agent|ci"},
    ],
)
def test_valid_elements_produce_no_findings(action):
    assert validate_actions([action]) == []


@pytest.mark.parametrize(
    "override, fragment",
    [
        ({"type": "refactor"}, "`type` fuera de dominio"),
        ({"status": "done"}, "`status` fuera de dominio"),
        ({"type": ["analysis"]}, "`type` fuera de dominio"),
        ({"actor": "robot"}, "fuera de DEFINITIONS.md"),
        ({"actor": f"human | {ACTOR_PROHIBITION}"}, "no admite combinar"),
        ({"actor": "human | human"}, "repite etiquetas"),
        ({"actor": 3}, "debe ser una etiqueta"),
        ({"deliverable": 7}, "`deliverable`"),
        ({"depends_on": "AC-00002"}, "`depends_on` debe ser una lista"),
        ({"depends_on": ["AC-002"]}, "`depends_on` contiene una referencia inválida"),
        ({"evidence": ["EVD-0007"]}, "`evidence` contiene una referencia inválida"),
        ({"evidence": [None]}, "`evidence` contiene una referencia inválida"),
        ({"owner": "human"}, "campo ajeno al esquema: 'owner'"),
    ],
)
def test_invalid_values_are_reported(override, fragment):
    findings = validate_actions([{**VALID, **override}])
    assert len(findings) == 1
    assert fragment in findings[0]
    assert findings[0].startswith("AC-00001:")


def test_missing_and_malformed_identifier():
    assert "falta el identificador" in validate_actions([{"type": "plan"}])[0]
    assert "identificador inválido: 'AC-001'" in validate_actions([{"id": "AC-001"}])[0]
    assert "actions[1]" in validate_actions([{"id": "AC-001"}])[0]


def test_duplicate_identifier_names_both_positions():
    findings = validate_actions([{"id": "AC-00001"}, {"id": "AC-00001"}])
    assert findings == ["AC-00001: identificador repetido; ya aparece en actions[1]."]


def test_element_that_is_not_a_mapping():
    assert validate_actions(["AC-00001"]) == ["actions[1]: debe ser un mapeo, no str."]


def test_several_findings_accumulate_per_element():
    findings = validate_actions([{"id": "AC-00001", "type": "refactor", "status": "done"}])
    assert len(findings) == 2


def test_actions_must_be_a_list():
    with pytest.raises(ActionSchemaError, match="debe ser una lista"):
        validate_actions({"id": "AC-00001"})


def test_document_without_actions_block():
    with pytest.raises(ActionSchemaError, match="Ningún bloque"):
        extract_actions("# RFC\n\n```yaml\nrfc: \"\"\n```\n")


def test_document_with_two_actions_blocks():
    text = document([]) + "\n" + document([])
    with pytest.raises(ActionSchemaError, match="ambiguo"):
        extract_actions(text)


def test_unreadable_yaml_block():
    with pytest.raises(ActionSchemaError, match="ilegible"):
        extract_actions("```yaml\nactions: [\n```\n")


def test_metadata_block_is_ignored():
    assert extract_actions(document([])) == []


def test_validate_rfc_actions_reads_the_document():
    assert validate_rfc_actions(document([VALID])) == []
    assert "`type` fuera de dominio" in validate_rfc_actions(document([{**VALID, "type": "x"}]))[0]
