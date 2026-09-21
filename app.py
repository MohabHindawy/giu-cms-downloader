import sys


def main():
    if "--headless" in sys.argv:
        from core.auth import get_session
        from core.config import BASE_URL
        from core.course_config import load_mapping, read_env
        from core.downloader import download_all
        from core.scraper import get_course_files, get_courses

        env = read_env()
        mapping = load_mapping()
        session = get_session(env["GIU_USERNAME"], env["GIU_PASSWORD"])
        courses = get_courses(session, BASE_URL)
        all_files = []
        has_errors = False
        for course in courses:
            try:
                all_files.extend(get_course_files(session, BASE_URL, course))
            except Exception as e:
                has_errors = True
                print(
                    f"Warning: Failed to fetch files for {course.code} - {e}",
                    file=sys.stderr,
                )

        if env.get("IGNORE_OLD_FILES") == "1":
            from core.downloader import mark_all_as_seen

            mark_all_as_seen(all_files)
            if not has_errors:
                env["IGNORE_OLD_FILES"] = "0"
                from core.course_config import write_env

                write_env(env)
            return

        download_all(session, all_files, mapping)
        return

    start_in_tray = "--tray" in sys.argv

    from core.single_instance import check_and_bind, start_listener

    server = check_and_bind()

    from ui.main_window import MainWindow

    app = MainWindow(start_in_tray=start_in_tray)

    start_listener(server, app)
    app.mainloop()


if __name__ == "__main__":
    main()
