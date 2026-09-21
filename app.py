import sys

def main():
    if "--headless" in sys.argv:
        from core.auth import get_session
        from core.scraper import get_courses, get_course_files
        from core.downloader import download_all
        from core.course_config import load_mapping, read_env
        from core.config import BASE_URL

        env = read_env()
        mapping = load_mapping()
        session = get_session(env["GIU_USERNAME"], env["GIU_PASSWORD"])
        courses = get_courses(session, BASE_URL)
        all_files = []
        for course in courses:
            all_files.extend(get_course_files(session, BASE_URL, course))
        download_all(session, all_files, mapping)
        return

    from ui.main_window import MainWindow
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()