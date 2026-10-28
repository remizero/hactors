from pathlib import Path

import yaml

COUNTER_FORMAT = "{prefix}_{number:06d}"


def next_counter_id(manifest_path: Path, counter_name: str, prefix: str) -> tuple[str, int]:
    with manifest_path.open() as f:
        data = yaml.safe_load(f)

    counters = data.get("counters", {})
    current = counters.get(counter_name, 0)
    new_value = current + 1

    counters[counter_name] = new_value
    data["counters"] = counters

    with manifest_path.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    formatted = COUNTER_FORMAT.format(prefix=prefix, number=new_value)
    return formatted, new_value
