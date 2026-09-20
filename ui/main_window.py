import queue
import customtkinter as ctk

from paths import get_app_dir
from ui.worker import DownloadWorker

customtkinter = ctk

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GIU CMS Downloader")
        self.geometry("800x500")

        self.update_queue = queue.Queue()
        self.worker = None

        env_path = get_app_dir() / ".env"
        mapping_path = get_app_dir() / "course_mapping.json"

        if env_path.exists() and mapping_path.exists():
            self.build_main_layout()
        else:
            self.build_login_only()


    def build_login_only(self):
        from ui.pages.login_page import LoginPage
        self.login_frame = LoginPage(self, on_success=self._on_setup_complete)
        self.login_frame.pack(fill="both", expand=True)

    def _on_setup_complete(self):
        self.login_frame.destroy()
        self.build_main_layout()

    def build_main_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=140)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew")

        self.run_bar = ctk.CTkFrame(self, height=70)
        self.run_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self._build_run_bar()

        for name in ("Courses", "Templates", "Blocking"):
            btn = ctk.CTkButton(self.sidebar, text=name, command=lambda n=name: self.show_page(n))
            btn.pack(fill="x", padx=10, pady=5)

        self.show_page("Courses")

    def _build_run_bar(self):
        self.run_button = ctk.CTkButton(self.run_bar, text="Run Now", command=self.start_run)
        self.run_button.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.run_bar, text="Idle", anchor="w")
        self.status_label.grid(row=0, column=1, sticky="w", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.run_bar, width=300)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=1, sticky="w", padx=10)

        self.size_label = ctk.CTkLabel(self.run_bar, text="")
        self.size_label.grid(row=1, column=2, sticky="w", padx=10)

    def show_page(self, name: str):
        for widget in self.content.winfo_children():
            widget.destroy()

        if name == "Courses":
            from ui.pages.courses_page import CoursesPage
            CoursesPage(self.content).pack(fill="both", expand=True)
        elif name == "Templates":
            from ui.pages.templates_page import TemplatesPage
            TemplatesPage(self.content).pack(fill="both", expand=True)
        elif name == "Blocking":
            from ui.pages.blocking_page import BlockingPage
            BlockingPage(self.content).pack(fill="both", expand=True)


    def start_run(self):
        self.run_button.configure(state="disabled")
        self.status_label.configure(text="Starting...")
        self.worker = DownloadWorker(self.update_queue)
        self.worker.start()
        self.after(100, self.poll_queue)

    def poll_queue(self):
        try:
            while True:
                message = self.update_queue.get_nowait()
                self._handle_message(message)
        except queue.Empty:
            pass

        if self.worker and self.worker.is_alive():
            self.after(100, self.poll_queue)

    def _handle_message(self, message):
        kind = message[0]

        if kind == "status":
            self.status_label.configure(text=message[1])

        elif kind == "scan_done":
            self.status_label.configure(text=f"Found {message[1]} files")

        elif kind == "file_start":
            title, done, total = message[1], message[2], message[3]
            self.status_label.configure(text=f"Downloading: {title} ({done}/{total})")
            self.progress_bar.set(0)
            self.size_label.configure(text="")

        elif kind == "file_progress":
            done_bytes, total_bytes = message[1], message[2]
            if total_bytes:
                self.progress_bar.set(done_bytes / total_bytes)
                self.size_label.configure(
                    text=f"{done_bytes / 1_048_576:.1f} MB / {total_bytes / 1_048_576:.1f} MB"
                )
            else:
                self.progress_bar.configure(mode="indeterminate")

        elif kind in ("file_done", "file_skipped", "file_blocked", "file_failed"):
            self.progress_bar.set(1)

        elif kind == "run_complete":
            self.status_label.configure(text="Done")
            self.progress_bar.set(0)
            self.run_button.configure(state="normal")

        elif kind == "fatal_error":
            self.status_label.configure(text=f"Error: {message[1]}")
            self.run_button.configure(state="normal")