from dataclasses import dataclass

@dataclass
class Course:
    code: str
    name: str
    id: str
    season_id: str

@dataclass
class CourseFile:
    course: Course
    week_label: str
    number: str
    title: str
    item_type: str
    content_id: str
    url: str