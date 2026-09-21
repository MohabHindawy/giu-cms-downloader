import queue
import threading

from core.auth import get_session
from core.config import BASE_URL
from core.course_config import load_mapping, read_env, write_env
from core.downloader import download_all, mark_all_as_seen
from core.scraper import get_course_files, get_courses


class DownloadWorker(threading.Thread):
    def __init__(self, update_queue: queue.Queue):
        super().__init__(daemon=True)
        self.queue = update_queue

    def run(self):
        try:
            env = read_env()
            mapping = load_mapping()
            session = get_session(env["GIU_USERNAME"], env["GIU_PASSWORD"])

            self.queue.put(("status", "Fetching course list..."))
            courses = get_courses(session, BASE_URL)

            all_files = []
            has_errors = False
            for course in courses:
                self.queue.put(("status", f"Scanning {course.code}..."))
                try:
                    files = get_course_files(session, BASE_URL, course)
                    all_files.extend(files)
                except Exception as e:
                    has_errors = True
                    self.queue.put(("log", f"Couldn't read {course.code}: {e}"))

            if env.get("IGNORE_OLD_FILES") == "1":
                self.queue.put(("status", "Marking existing files as seen..."))
                mark_all_as_seen(all_files)
                if not has_errors:
                    env["IGNORE_OLD_FILES"] = "0"
                    write_env(env)
                    self.queue.put(
                        ("status", "Existing CMS files marked as already downloaded")
                    )
                else:
                    self.queue.put(
                        ("status", "Marked files, but kept flag due to errors")
                    )
                self.queue.put(("run_complete",))
                return

            total = len(all_files)
            self.queue.put(("scan_done", total))

            completed = 0

            def on_event(event, **kwargs):
                nonlocal completed
                if event == "start":
                    self.queue.put(
                        ("file_start", kwargs["file"].title, completed, total)
                    )
                elif event == "progress":
                    self.queue.put(("file_progress", kwargs["done"], kwargs["total"]))
                elif event == "done":
                    completed += 1
                    self.queue.put(
                        ("file_done", kwargs["file"].title, completed, total)
                    )
                elif event == "skipped":
                    completed += 1
                    self.queue.put(
                        ("file_skipped", kwargs["file"].title, kwargs["reason"])
                    )
                elif event == "blocked":
                    completed += 1
                    self.queue.put(
                        ("file_blocked", kwargs["file"].title, kwargs["reason"])
                    )
                elif event == "failed":
                    completed += 1
                    self.queue.put(
                        ("file_failed", kwargs["file"].title, kwargs["error"])
                    )

            download_all(session, all_files, mapping, on_event=on_event)
            self.queue.put(("run_complete", None))

        except Exception as e:
            self.queue.put(("fatal_error", str(e)))
