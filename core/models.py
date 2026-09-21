from dataclasses import dataclass

@dataclass
class Course:
    code: str
    name: str
    id: str
    season_id: str
    season: str

@dataclass
class CourseFile:
    course: Course
    title: str
    item_type: str
    content_id: str
    url: str