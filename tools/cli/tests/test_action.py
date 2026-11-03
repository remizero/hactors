from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from hactors_cli.cli import cli
from hactors_cli.core.action import (
    ACTION_FIELDS,
    ACTION_STATUSES,
    ACTION_TYPES,
    ACTOR_LABELS,
    ACTOR_PROHIBITION,
    ActionError,
    ActionSchemaError,
    append_action,
    create_action,
    extract_actions,
    validate_actions,
    validate_rfc_actions,
)
from hactors_cli.core.documents import yaml_blocks
from hactors_cli.core.project import create_project

SPECS_TEMPLATES = Path(__file__).resolve().parents[3] / "specs" / "templates"
SPECS = SPECS_TEMPLATES.parent

VALID = {
    "id": "ACT-00001",
    "type": "implementation",
    "status": "in-progress",
    "actor": "human | agent",
    "depends_on": ["ACT-00002"],
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
    assert table_first_column(SPECS_TEMPLATES / "ACT_TEMPLATE.md", "Tipos") == set(ACTION_TYPES)


def test_statuses_match_ac_template():
    assert table_first_column(SPECS_TEMPLATES / "ACT_TEMPLATE.md", "Estados") == set(ACTION_STATUSES)


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
        {"id": "ACT-00001"},
        {
            "id": "ACT-00001", "type": "", "status": "", "actor": "",
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
        ({"depends_on": "ACT-00002"}, "`depends_on` debe ser una lista"),
        ({"depends_on": ["ACT-002"]}, "`depends_on` contiene una referencia inválida"),
        ({"evidence": ["EVD-0007"]}, "`evidence` contiene una referencia inválida"),
        ({"evidence": [None]}, "`evidence` contiene una referencia inválida"),
        ({"owner": "human"}, "campo ajeno al esquema: 'owner'"),
    ],
)
def test_invalid_values_are_reported(override, fragment):
    findings = validate_actions([{**VALID, **override}])
    assert len(findings) == 1
    assert fragment in findings[0]
    assert findings[0].startswith("ACT-00001:")


def test_missing_and_malformed_identifier():
    assert "falta el identificador" in validate_actions([{"type": "plan"}])[0]
    assert "identificador inválido: 'ACT-001'" in validate_actions([{"id": "ACT-001"}])[0]
    assert "actions[1]" in validate_actions([{"id": "ACT-001"}])[0]


def test_duplicate_identifier_names_both_positions():
    findings = validate_actions([{"id": "ACT-00001"}, {"id": "ACT-00001"}])
    assert findings == ["ACT-00001: identificador repetido; ya aparece en actions[1]."]


def test_element_that_is_not_a_mapping():
    assert validate_actions(["ACT-00001"]) == ["actions[1]: debe ser un mapeo, no str."]


def test_several_findings_accumulate_per_element():
    findings = validate_actions([{"id": "ACT-00001", "type": "refactor", "status": "done"}])
    assert len(findings) == 2


def test_actions_must_be_a_list():
    with pytest.raises(ActionSchemaError, match="debe ser una lista"):
        validate_actions({"id": "ACT-00001"})


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


RFC_PATH = "rfcs/RFC-A00001.md"


def invoke(root, *args, expected=0):
    result = CliRunner().invoke(cli, [*args, "--root", str(root)])
    assert result.exit_code == expected, result.output
    assert "Traceback" not in result.output
    return result


def counters(project: Path) -> dict:
    return yaml.safe_load((project / "manifest.yaml").read_text())["counters"]


def set_counter(project: Path, name: str, value: int) -> None:
    manifest = project / "manifest.yaml"
    data = yaml.safe_load(manifest.read_text())
    data["counters"][name] = value
    manifest.write_text(yaml.dump(data, sort_keys=False))


def rfc_file(project: Path, actions=None) -> Path:
    path = project / RFC_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document([] if actions is None else actions))
    set_counter(project, "rfc_a", 1)
    return path


@pytest.fixture
def project(hactors_root):
    created = create_project("proj", hactors_root)
    invoke(hactors_root, "use-project", created.name)
    return created


def test_the_action_template_reproduces_the_rfc_template_element():
    section = (SPECS_TEMPLATES / "RFC_TEMPLATE.md").read_text().split("## Acciones derivadas\n", 1)[1]
    documented = yaml_blocks(section.split("\n## ", 1)[0])[0]["actions"][0]
    template = yaml.safe_load((SPECS_TEMPLATES / "action_template.yaml").read_text())
    assert set(template) == set(ACTION_FIELDS)
    assert documented == {**template, "id": "ACT-00001"}
    assert validate_actions([documented]) == []


def test_append_action_expands_an_empty_flow_list():
    updated = append_action('```yaml\nactions: []\nmigration_plan: ""\n```\n', {"id": "ACT-00001"})
    assert extract_actions(updated) == [{"id": "ACT-00001"}]
    assert 'migration_plan: ""' in updated


def test_append_action_keeps_the_indentation_of_the_list():
    text = '```yaml\nactions:\n    - id: ACT-00007\n      type: plan\nother: ""\n```\n'
    updated = append_action(text, {"id": "ACT-00001"})
    assert extract_actions(updated) == [{"id": "ACT-00007", "type": "plan"}, {"id": "ACT-00001"}]
    assert "    - id: ACT-00001\n" in updated
    assert updated.index("    - id: ACT-00001") < updated.index('other: ""')


def test_create_action_appends_the_element(hactors_root, project):
    path = rfc_file(project)
    action_id, written = create_action(
        hactors_root, project.name, RFC_PATH, type_="plan", actor="agent", deliverable="plans/x.md"
    )
    assert (action_id, written) == ("ACT-00001", path)
    assert extract_actions(path.read_text()) == [
        {
            "id": "ACT-00001", "type": "plan", "status": "pending", "actor": "agent",
            "depends_on": [], "deliverable": "plans/x.md", "evidence": [],
        }
    ]
    assert counters(project)["action"] == 1


def test_create_action_keeps_the_template_defaults(hactors_root, project):
    path = rfc_file(project)
    create_action(hactors_root, project.name, RFC_PATH)
    template = yaml.safe_load((SPECS_TEMPLATES / "action_template.yaml").read_text())
    assert extract_actions(path.read_text()) == [{**template, "id": "ACT-00001"}]


def test_create_action_appends_after_the_declared_actions(hactors_root, project):
    path = rfc_file(project, actions=[VALID])
    set_counter(project, "action", 1)
    before = path.read_text()
    action_id, _ = create_action(hactors_root, project.name, RFC_PATH, type_="test")
    assert action_id == "ACT-00002"
    assert [action["id"] for action in extract_actions(path.read_text())] == ["ACT-00001", "ACT-00002"]
    head, tail = before.split("actions:\n", 1)
    after = path.read_text()
    assert after.startswith(head + "actions:\n" + tail.split("```\n")[0])
    assert after.endswith("```\n")


def test_create_action_registers_the_repeated_options(hactors_root, project):
    path = rfc_file(project)
    create_action(
        hactors_root, project.name, RFC_PATH,
        depends_on=("ACT-00007", "ACT-00008"), evidence=("EVD-00003",),
    )
    declared = extract_actions(path.read_text())[0]
    assert declared["depends_on"] == ["ACT-00007", "ACT-00008"]
    assert declared["evidence"] == ["EVD-00003"]


@pytest.mark.parametrize(
    "options, fragment",
    [
        ({"type_": "refactor"}, "`type` fuera de dominio"),
        ({"status": "done"}, "`status` fuera de dominio"),
        ({"actor": "robot"}, "fuera de DEFINITIONS.md"),
        ({"actor": f"human | {ACTOR_PROHIBITION}"}, "no admite combinar"),
        ({"depends_on": ("ACT-002",)}, "`depends_on` contiene una referencia inválida"),
        ({"evidence": ("EVD-0007",)}, "`evidence` contiene una referencia inválida"),
        ({"deliverable": 7}, "`deliverable`"),
    ],
)
def test_create_action_rejects_values_outside_the_schema(hactors_root, project, options, fragment):
    path = rfc_file(project)
    with pytest.raises(ActionError) as excinfo:
        create_action(hactors_root, project.name, RFC_PATH, **options)
    assert fragment in str(excinfo.value)
    assert extract_actions(path.read_text()) == []


def test_a_rejected_value_consumes_the_counter(hactors_root, project):
    rfc_file(project)
    with pytest.raises(ActionError):
        create_action(hactors_root, project.name, RFC_PATH, type_="refactor")
    assert counters(project)["action"] == 1


def test_create_action_rejects_an_identifier_already_declared(hactors_root, project):
    rfc_file(project, actions=[VALID])
    with pytest.raises(ActionError) as excinfo:
        create_action(hactors_root, project.name, RFC_PATH)
    assert "produciría un identificador ya declarado en la RFC: 'ACT-00001'." in str(excinfo.value)
    assert counters(project)["action"] == 0


@pytest.mark.parametrize(
    "text, fragment",
    [
        ('```yaml\nrfc: "RFC-A00001"\n```\n', "Ningún bloque `yaml` del documento declara"),
        (document([]) + "\n" + document([]), "el documento es ambiguo"),
        ('```yaml\nrfc: "RFC-A00001"\n```\n\n```yaml\nactions: [{id: ACT-00007}]\n```\n',
         "no está en forma de bloque"),
        ('```yaml\nrfc: "RFC-A00001"\n```\n\n```yaml\n{actions: []}\n```\n',
         "no está en el nivel superior del bloque"),
        ('```yaml\nstatus: draft\n```\n', "no declara el campo 'rfc:'"),
    ],
)
def test_create_action_rejects_a_document_it_cannot_extend(hactors_root, project, text, fragment):
    path = rfc_file(project)
    path.write_text(text)
    with pytest.raises(ActionError) as excinfo:
        create_action(hactors_root, project.name, RFC_PATH)
    assert fragment in str(excinfo.value)
    assert path.read_text() == text


def test_a_document_that_cannot_be_extended_consumes_the_counter(hactors_root, project):
    path = rfc_file(project)
    path.write_text('```yaml\nrfc: "RFC-A00001"\n```\n\n```yaml\nactions: [{id: ACT-00007}]\n```\n')
    with pytest.raises(ActionError):
        create_action(hactors_root, project.name, RFC_PATH)
    assert counters(project)["action"] == 1


@pytest.mark.parametrize("origin", ["rfcs", "/etc/passwd", "rfcs/../manifest.yaml", "rfcs/ausente.md"])
def test_create_action_rejects_an_origin_that_is_not_an_rfc_file(hactors_root, project, origin):
    rfc_file(project)
    with pytest.raises(ActionError):
        create_action(hactors_root, project.name, origin)
    assert counters(project)["action"] == 0


def test_command_registers_the_action(hactors_root, project):
    rfc_file(project)
    result = invoke(
        hactors_root, "create-action", "--rfc", RFC_PATH, "--type", "implementation", "--actor", "agent"
    )
    assert f"Acción ACT-00001 registrada en: {project / RFC_PATH}" in result.output
    assert counters(project)["action"] == 1


def test_command_requires_the_rfc(hactors_root, project):
    invoke(hactors_root, "create-action", "--type", "plan", expected=2)


def test_command_reports_a_value_outside_the_schema(hactors_root, project):
    rfc_file(project)
    result = invoke(hactors_root, "create-action", "--rfc", RFC_PATH, "--type", "refactor", expected=1)
    assert "`type` fuera de dominio" in result.output


def test_command_requires_an_active_project(hactors_root):
    result = invoke(hactors_root, "create-action", "--rfc", RFC_PATH, expected=1)
    assert "No hay proyecto activo." in result.output


def test_the_created_action_leaves_the_project_consistent(hactors_root, project):
    rfc_file(project)
    invoke(hactors_root, "create-action", "--rfc", RFC_PATH, "--type", "plan", "--actor", "human")
    assert "sin inconsistencias" in invoke(hactors_root, "validate").output
