from auth import get_session
from scraper import get_courses, get_course_files
from downloader import download_all
from config import GIU_USERNAME, GIU_PASSWORD, BASE_URL, DOWNLOAD_ROOT


def main():
    session = get_session(GIU_USERNAME, GIU_PASSWORD)

    print("Fetching course list...")
    courses = get_courses(session, BASE_URL)
    print(f"Found {len(courses)} courses.\n")

    all_files = []
    for course in courses:
        print(f"Scanning {course.code} - {course.name}...")
        files = get_course_files(session, BASE_URL, course)
        print(f"  found {len(files)} items")
        all_files.extend(files)

    print(f"\nTotal items across all courses: {len(all_files)}")
    download_all(session, all_files, DOWNLOAD_ROOT)


if __name__ == "__main__":
    main()