import json
from dataclasses import dataclass, asdict
from pathlib import Path

ENV_FILE = ".env"
MAPPING_FILE = "course_mapping.json"


@dataclass
class CourseConfig:
    display_name: str
    folder: str
    flat: bool


def load_mapping() -> dict[str, CourseConfig]:
    path = Path(MAPPING_FILE)
    if not path.exists():
        return {}
    with path.open("r") as f:
        raw = json.load(f)
    return {code: CourseConfig(**data) for code, data in raw.items()}


def save_mapping(mapping: dict[str, CourseConfig]) -> None:
    raw = {code: asdict(cfg) for code, cfg in mapping.items()}
    with Path(MAPPING_FILE).open("w") as f:
        json.dump(raw, f, indent=2)


def read_env() -> dict[str, str]:
    path = Path(ENV_FILE)
    values = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def write_env(values: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in values.items()]
    Path(ENV_FILE).write_text("\n".join(lines) + "\n")