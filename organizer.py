import re
from pathlib import PurePosixPath
from models import CourseFile

INVALID_CHARS = re.compile(r'[<>:"/\\|?*]')

def sanitize(name: str) -> str:
    return INVALID_CHARS.sub("", name).strip()

def folder_path(cf: CourseFile) -> str:
    course_folder = sanitize(cf.course.name)
    type_folder = sanitize(cf.item_type) or "Other"
    return f"{course_folder}/{type_folder}"

def file_name(cf: CourseFile) -> str:
    ext = PurePosixPath(cf.url).suffix
    title = sanitize(cf.title)
    return f"{cf.number} - {title}{ext}"