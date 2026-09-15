from auth import get_session
from scraper import get_courses, get_course_files
from downloader import download_all
from course_config import load_mapping
from config import GIU_USERNAME, GIU_PASSWORD, BASE_URL


def main():
    mapping = load_mapping()
    if not mapping:
        print("No course configuration found. Run setup-wizard.exe first.")
        return

    try:
        session = get_session(GIU_USERNAME, GIU_PASSWORD)

        print("Fetching course list...")
        courses = get_courses(session, BASE_URL)
    except Exception as e:
        print(f"Couldn't reach the CMS or log in: {e}")
        print("If your password recently changed, run setup-wizard.exe again.")
        return

    unconfigured = [c for c in courses if c.code not in mapping]
    if unconfigured:
        print("New courses found that aren't configured yet:")
        for c in unconfigured:
            print(f"  {c.code} - {c.name}")
        print("Run setup-wizard.exe to configure them.\n")

    all_files = []
    for course in courses:
        print(f"Scanning {course.code} - {course.name}...")
        try:
            files = get_course_files(session, BASE_URL, course)
        except Exception as e:
            print(f"  Couldn't read this course, skipping: {e}")
            continue
        all_files.extend(files)

    download_all(session, all_files, mapping)


if __name__ == "__main__":
    main()