import json
from dataclasses import dataclass, asdict, field
from paths import get_app_dir

TEMPLATES_FILE = get_app_dir() / "templates.json"

DEFAULT_TEMPLATE_NAME = "Default"


@dataclass
class StructureTemplate:
    name: str
    groups: dict[str, list[str]] = field(default_factory=dict)

    def folder_for(self, item_type: str) -> str:
        for group_name, types in self.groups.items():
            if item_type in types:
                return group_name
        return "Other"


def _default_template() -> StructureTemplate:
    return StructureTemplate(
        name=DEFAULT_TEMPLATE_NAME,
        groups={
            "Lectures": ["Lecture slides", "Lecture Notes"],
            "Assignments": ["Assignment", "Homework"],
            "Labs": ["Lab"],
            "Solutions": ["Solution"],
        },
    )


def load_templates() -> dict[str, StructureTemplate]:
    if not TEMPLATES_FILE.exists():
        default = _default_template()
        save_templates({default.name: default})
        return {default.name: default}

    with TEMPLATES_FILE.open("r") as f:
        raw = json.load(f)
    return {name: StructureTemplate(**data) for name, data in raw.items()}


def save_templates(templates: dict[str, StructureTemplate]) -> None:
    raw = {name: asdict(t) for name, t in templates.items()}
    tmp = TEMPLATES_FILE.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(raw, f, indent=2)
    tmp.replace(TEMPLATES_FILE)