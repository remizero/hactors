import re

import yaml

YAML_BLOCK = re.compile(r"^```ya?ml[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
FRONTMATTER = "---\n"


class DocumentError(Exception):
    pass


def yaml_blocks(text: str) -> list:
    blocks = []
    for block in YAML_BLOCK.findall(text):
        try:
            blocks.append(yaml.safe_load(block))
        except yaml.YAMLError as exc:
            raise DocumentError(f"Bloque `yaml` ilegible: {exc}") from exc
    return blocks


def front_matter(text: str) -> dict:
    if not text.startswith(FRONTMATTER):
        raise DocumentError("El documento no empieza con una cabecera frontmatter.")
    header = text[len(FRONTMATTER) :].split("\n---\n", 1)[0]
    try:
        data = yaml.safe_load(header)
    except yaml.YAMLError as exc:
        raise DocumentError(f"Cabecera frontmatter ilegible: {exc}") from exc
    if not isinstance(data, dict):
        raise DocumentError("La cabecera frontmatter no es un mapeo YAML.")
    return data


def document_identity(text: str, field: str):
    for block in yaml_blocks(text):
        if isinstance(block, dict) and block.get(field):
            return block[field]
    return None
