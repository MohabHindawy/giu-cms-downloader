import re
from pathlib import Path
from urllib.parse import urlparse, unquote
from core.models import CourseFile
from core.course_config import CourseConfig
from core.templates import load_templates

INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def sanitize(name: str) -> str:
    name = INVALID_CHARS.sub("", name).strip()
    name = name.rstrip(". ")
    if not name:
        name = "untitled"
    if name.split(".", 1)[0].upper() in RESERVED_NAMES:
        name = f"_{name}"
    return name


def get_extension(url: str) -> str:
    path = urlparse(url).path
    return Path(unquote(path)).suffix


def target_path(cf: CourseFile, cfg: CourseConfig) -> Path:
    base = Path(cfg.folder)
    if cfg.template_name != "Flat":
        templates = load_templates()
        template = templates.get(cfg.template_name)
        if template:
            folder = sanitize(template.folder_for(cf.item_type))
        else:
            folder = sanitize(cf.item_type or "Other")
        base = base / folder

    ext = get_extension(cf.url)
    name = f"{sanitize(cf.title)}{ext}"
    return base / name