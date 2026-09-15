import re
from pathlib import Path, PurePosixPath
from models import CourseFile
from course_config import CourseConfig

INVALID_CHARS = re.compile(r'[<>:"/\\|?*]')


def sanitize(name: str) -> str:
    return INVALID_CHARS.sub("", name).strip()


def target_path(cf: CourseFile, cfg: CourseConfig) -> Path:
    base = Path(cfg.folder)
    if not cfg.flat:
        base = base / sanitize(cf.item_type or "Other")

    ext = PurePosixPath(cf.url).suffix
    name = f"{cf.number} - {sanitize(cf.title)}{ext}"
    return base / name