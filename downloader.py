import json
from pathlib import Path
from models import CourseFile
from course_config import CourseConfig
from organizer import target_path

STATE_FILE = "state.json"


def load_state() -> set[str]:
    path = Path(STATE_FILE)
    if not path.exists():
        return set()
    with path.open("r") as f:
        return set(json.load(f))


def save_state(downloaded_ids: set[str]) -> None:
    with Path(STATE_FILE).open("w") as f:
        json.dump(sorted(downloaded_ids), f, indent=2)


def download_file(session, cf: CourseFile, cfg: CourseConfig) -> Path:
    path = target_path(cf, cfg)
    path.parent.mkdir(parents=True, exist_ok=True)

    resp = session.get(cf.url, stream=True)
    resp.raise_for_status()

    with path.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return path


def download_all(session, files: list[CourseFile], mapping: dict[str, CourseConfig]) -> None:
    downloaded_ids = load_state()

    for cf in files:
        if cf.content_id in downloaded_ids:
            print(f"Skipping (already downloaded): {cf.title}")
            continue

        cfg = mapping.get(cf.course.code)
        if cfg is None:
            print(f"Skipping (not configured): {cf.course.code} - {cf.title}")
            continue

        print(f"Downloading: {cf.title} ...")
        try:
            path = download_file(session, cf, cfg)
            print(f"  -> saved to {path}")
            downloaded_ids.add(cf.content_id)
            save_state(downloaded_ids)
        except Exception as e:
            print(f"  FAILED: {e}")