import json
from pathlib import Path
from models import CourseFile
from organizer import folder_path, file_name

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


def download_file(session, cf: CourseFile, download_root: str) -> Path:
    target_dir = Path(download_root) / folder_path(cf)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / file_name(cf)

    resp = session.get(cf.url, stream=True)
    resp.raise_for_status()

    with target_path.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return target_path


def download_all(session, files: list[CourseFile], download_root: str) -> None:
    downloaded_ids = load_state()

    for cf in files:
        if cf.content_id in downloaded_ids:
            print(f"Skipping (already downloaded): {cf.title}")
            continue

        print(f"Downloading: {cf.title} ...")
        try:
            path = download_file(session, cf, download_root)
            print(f"  -> saved to {path}")
            downloaded_ids.add(cf.content_id)
            save_state(downloaded_ids)
        except Exception as e:
            print(f"  FAILED: {e}")