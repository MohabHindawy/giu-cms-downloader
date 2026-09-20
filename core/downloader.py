import json
from pathlib import Path
from core.models import CourseFile
from core.course_config import CourseConfig
from core.organizer import target_path
from core.blocking import load_rules, is_blocked
from paths import get_app_dir
from core.config import REQUEST_TIMEOUT

STATE_FILE = get_app_dir() / "state.json"


def load_state() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    with STATE_FILE.open("r") as f:
        return set(json.load(f))


def save_state(downloaded_ids: set[str]) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(sorted(downloaded_ids), f, indent=2)
    tmp.replace(STATE_FILE)


def mark_all_as_seen(files: list[CourseFile]) -> None:
    ids = load_state()
    for cf in files:
        ids.add(cf.content_id)
    save_state(ids)


def download_file(session, cf: CourseFile, cfg: CourseConfig) -> Path:
    path = target_path(cf, cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".part")

    resp = session.get(cf.url, stream=True, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    with tmp_path.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    tmp_path.replace(path)
    return path


def download_all(session, files: list[CourseFile], mapping: dict[str, CourseConfig]) -> None:
    downloaded_ids = load_state()
    rules = load_rules()

    for cf in files:
        if cf.content_id in downloaded_ids:
            print(f"Skipping (already downloaded): {cf.title}")
            continue

        cfg = mapping.get(cf.course.code)
        if cfg is None:
            print(f"Skipping (not configured): {cf.course.code} - {cf.title}")
            continue

        if rules:
            reason = is_blocked(session, cf, rules, REQUEST_TIMEOUT)
            if reason:
                print(f"Blocked ({reason}): {cf.title}")
                continue

        print(f"Downloading: {cf.title} ...")
        try:
            path = download_file(session, cf, cfg)
            print(f"  -> saved to {path}")
            downloaded_ids.add(cf.content_id)
            save_state(downloaded_ids)
        except Exception as e:
            print(f"  FAILED: {e}")