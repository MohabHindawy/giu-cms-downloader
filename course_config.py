import json
from dataclasses import dataclass, asdict
from paths import get_app_dir

ENV_FILE = get_app_dir() / ".env"
MAPPING_FILE = get_app_dir() / "course_mapping.json"


@dataclass
class CourseConfig:
    display_name: str
    folder: str
    flat: bool


def load_mapping() -> dict[str, CourseConfig]:
    if not MAPPING_FILE.exists():
        return {}
    with MAPPING_FILE.open("r") as f:
        raw = json.load(f)
    return {code: CourseConfig(**data) for code, data in raw.items()}


def save_mapping(mapping: dict[str, CourseConfig]) -> None:
    raw = {code: asdict(cfg) for code, cfg in mapping.items()}
    tmp = MAPPING_FILE.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(raw, f, indent=2)
    tmp.replace(MAPPING_FILE)


def read_env() -> dict[str, str]:
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def write_env(values: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in values.items()]
    tmp = ENV_FILE.with_suffix(".tmp")
    tmp.write_text("\n".join(lines) + "\n")
    tmp.replace(ENV_FILE)