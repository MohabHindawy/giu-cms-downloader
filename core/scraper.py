import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from models import Course, CourseFile
from config import REQUEST_TIMEOUT

COURSE_LIST_URL = "/apps/student/HomePageStn.aspx"
COURSE_ROW_RE = re.compile(r"\(\|(?P<code>[^|]+)\|\)\s*(?P<name>.+?)\s*\(\d+\)\s*$")
SEASON_RE = re.compile(r"(?P<season>\w+)\s+(?P<year>\d{4})")

SEASON_ORDER = {"Spring": 0, "Summer": 1, "Winter": 2}


def _season_key(season_str: str) -> tuple[int, int]:
    m = SEASON_RE.match(season_str.strip())
    if not m:
        return (0, 0)
    year = int(m.group("year"))
    rank = SEASON_ORDER.get(m.group("season"), -1)
    return (year, rank)


def get_courses(session, base_url: str, latest_season_only: bool = True) -> list[Course]:
    resp = session.get(urljoin(base_url, COURSE_LIST_URL), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    table = soup.find("table", id=re.compile(r"GridViewcourses$"))
    if table is None:
        raise RuntimeError(
            "Couldn't find the course list on the CMS page. "
            "This usually means login failed, or the CMS page layout has changed."
        )

    courses = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 6:
            continue

        name_cell = cells[1].get_text(strip=True)
        season_str = cells[3].get_text(strip=True)
        course_id = cells[4].get_text(strip=True)
        season_id = cells[5].get_text(strip=True)

        m = COURSE_ROW_RE.match(name_cell)
        if not m:
            continue

        courses.append(Course(
            code=m.group("code"),
            name=m.group("name").strip(),
            id=course_id,
            season_id=season_id,
            season=season_str,
        ))

    if latest_season_only and courses:
        latest = max(_season_key(c.season) for c in courses)
        courses = [c for c in courses if _season_key(c.season) == latest]

    return courses