import json
from dataclasses import dataclass, asdict
from paths import get_app_dir
from core.models import CourseFile

RULES_FILE = get_app_dir() / "blocking_rules.json"


@dataclass
class BlockingRule:
    type: str
    value: str


def load_rules() -> list[BlockingRule]:
    if not RULES_FILE.exists():
        return []
    with RULES_FILE.open("r") as f:
        raw = json.load(f)
    return [BlockingRule(**r) for r in raw]


def save_rules(rules: list[BlockingRule]) -> None:
    raw = [asdict(r) for r in rules]
    tmp = RULES_FILE.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(raw, f, indent=2)
    tmp.replace(RULES_FILE)


def get_file_size_mb(session, url: str, timeout: int) -> float | None:
    try:
        resp = session.head(url, timeout=timeout, allow_redirects=True)
        size = resp.headers.get("Content-Length")
        if size is None:
            return None
        return int(size) / (1024 * 1024)
    except Exception:
        return None


def is_blocked(session, cf: CourseFile, rules: list[BlockingRule], timeout: int) -> str | None:
    for rule in rules:
        if rule.type == "name_contains":
            if rule.value.lower() in cf.title.lower():
                return f"title contains '{rule.value}'"

        elif rule.type == "size_over_mb":
            size_mb = get_file_size_mb(session, cf.url, timeout)
            if size_mb is not None and size_mb > float(rule.value):
                return f"file is {size_mb:.0f} MB (limit: {rule.value} MB)"

    return None