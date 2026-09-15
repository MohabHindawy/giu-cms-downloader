import json
from dataclasses import dataclass, asdict
from pathlib import Path

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