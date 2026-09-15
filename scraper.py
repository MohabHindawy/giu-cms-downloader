import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from models import Course, CourseFile

COURSE_LIST_URL = "/apps/student/HomePageStn.aspx"
COURSE_ROW_RE = re.compile(r"\(\|(?P<code>[^|]+)\|\)\s*(?P<name>.+?)\s*\(\d+\)\s*$")


def get_courses(session, base_url: str) -> list[Course]:
    resp = session.get(urljoin(base_url, COURSE_LIST_URL))
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    courses = []
    table = soup.find("table", id=re.compile(r"GridViewcourses$"))
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if not cells:
            continue

        name_cell = cells[1].get_text(strip=True)
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
        ))
    return courses


def get_course_files(session, base_url: str, course: Course) -> list[CourseFile]:
    url = urljoin(base_url, f"/apps/student/CourseViewStn.aspx?id={course.id}&sid={course.season_id}")
    resp = session.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    files = []
    for week_div in soup.select("div.card.mb-5.weeksdata"):
        header = week_div.select_one("h2.text-big")
        week_label = header.get_text(strip=True).removeprefix("Week:").strip() if header else "Unknown Week"

        for card in week_div.select("div.card.mb-4"):
            strong = card.find("strong")
            if not strong:
                continue

            number, _, title = strong.get_text(strip=True).partition(" - ")
            number, title = number.strip(), title.strip()

            content_div = card.select_one("div[id^='content']")
            item_type = ""
            if content_div:
                full_text = content_div.get_text(" ", strip=True)
                if "(" in full_text:
                    item_type = full_text.rsplit("(", 1)[-1].rstrip(")").strip()

            link = card.select_one("a#download")
            if not link or not link.get("href"):
                continue

            content_id = link.get("data-contentid", "")
            file_url = urljoin(base_url, link["href"])

            files.append(CourseFile(
                course=course,
                week_label=week_label,
                number=number,
                title=title,
                item_type=item_type,
                content_id=content_id,
                url=file_url,
            ))
    return files