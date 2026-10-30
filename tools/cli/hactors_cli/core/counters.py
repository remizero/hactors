import errno
from pathlib import Path

import yaml

COUNTER_FORMAT = "{prefix}_{number:06d}"
EVIDENCE_ID_FORMAT = "EVD-{number:05d}"
EVIDENCE_COUNTER = "evidence"
FINDING_ID_FORMAT = "FND-{number:05d}"
FINDING_COUNTER = "finding"


def _incremented_manifest(manifest_path: Path, counter_name: str) -> tuple[dict, int]:
    with manifest_path.open() as f:
        data = yaml.safe_load(f)

    counters = data.get("counters", {})
    if not isinstance(counters, dict):
        raise ValueError("Contadores inválidos en el manifest del proyecto.")
    current = counters.get(counter_name, 0)
    if type(current) is not int or current < 0:
        raise ValueError(f"Contador inválido: '{counter_name}'. Debe ser un entero no negativo.")
    new_value = current + 1

    counters[counter_name] = new_value
    data["counters"] = counters
    return data, new_value


def _persist(manifest_path: Path, data: dict) -> None:
    with manifest_path.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def next_counter_id(
    manifest_path: Path, counter_name: str, prefix: str, parent_dir: Path
) -> tuple[str, int]:
    data, new_value = _incremented_manifest(manifest_path, counter_name)
    formatted = COUNTER_FORMAT.format(prefix=prefix, number=new_value)
    ancestors = parent_dir.relative_to(manifest_path.parent / "hactors").parts
    if formatted in ancestors:
        raise ValueError(f"El contador '{counter_name}' produciría un ID ancestral repetido: '{formatted}'.")
    target = parent_dir / formatted
    if target.exists() or target.is_symlink():
        raise FileExistsError(errno.EEXIST, "Ya existe una instancia", str(target))

    _persist(manifest_path, data)
    return formatted, new_value


def _next_record_id(
    manifest_path: Path, counter_name: str, id_format: str, directory: Path
) -> tuple[str, int]:
    data, new_value = _incremented_manifest(manifest_path, counter_name)
    formatted = id_format.format(number=new_value)
    target = directory / f"{formatted}.yaml"
    if target.exists() or target.is_symlink():
        raise FileExistsError(errno.EEXIST, "Ya existe un registro", str(target))

    _persist(manifest_path, data)
    return formatted, new_value


def next_evidence_id(manifest_path: Path, directory: Path) -> tuple[str, int]:
    return _next_record_id(manifest_path, EVIDENCE_COUNTER, EVIDENCE_ID_FORMAT, directory)


def next_finding_id(manifest_path: Path, directory: Path) -> tuple[str, int]:
    return _next_record_id(manifest_path, FINDING_COUNTER, FINDING_ID_FORMAT, directory)
