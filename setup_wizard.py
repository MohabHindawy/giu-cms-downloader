from pathlib import Path
from auth import get_session
from scraper import get_courses
from course_config import load_mapping, save_mapping, CourseConfig
from config import GIU_USERNAME, GIU_PASSWORD, BASE_URL, DOWNLOAD_ROOT


def prompt_yes_no(question: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer.startswith("y")


def configure_course(course, existing: CourseConfig | None) -> CourseConfig:
    print(f"\n--- {course.code} - {course.name} ---")

    default_name = existing.display_name if existing else course.name
    name = input(f"Folder name for this course [{default_name}]: ").strip()
    display_name = name or default_name

    default_folder = existing.folder if existing else str(DOWNLOAD_ROOT / display_name)
    folder = input(f"Full folder path [{default_folder}]: ").strip()
    folder = folder or default_folder

    default_flat = existing.flat if existing else False
    flat = not prompt_yes_no(
        "Organize into subfolders by type (Lectures, Assignments, etc.)?",
        default=not default_flat,
    )

    return CourseConfig(display_name=display_name, folder=folder, flat=flat)


def main():
    session = get_session(GIU_USERNAME, GIU_PASSWORD)
    print("Fetching your courses...")
    courses = get_courses(session, BASE_URL)

    mapping = load_mapping()

    print(f"\nFound {len(courses)} courses. Configure each one below.")
    print("Press Enter on any question to accept the default shown in [brackets].\n")

    for course in courses:
        existing = mapping.get(course.code)
        mapping[course.code] = configure_course(course, existing)

    save_mapping(mapping)
    print(f"\nSaved configuration for {len(mapping)} courses to course_mapping.json.")


if __name__ == "__main__":
    main()