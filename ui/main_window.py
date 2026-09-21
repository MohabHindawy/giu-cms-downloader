import queue
import customtkinter as ctk

from paths import get_app_dir
from ui.worker import DownloadWorker

import sys

_old_mouse_wheel_all = ctk.CTkScrollableFrame._mouse_wheel_all
def _patched_mouse_wheel_all(self, event):
    if self._check_if_valid_scroll(event.widget):
        if sys.platform.startswith("linux") and getattr(event, "num", 0) not in (4, 5) and getattr(event, "delta", 0) != 0:
            direction = -1 if event.delta > 0 else 1
            if self._shift_pressed:
                if self._parent_canvas.xview() != (0.0, 1.0):
                    self._parent_canvas.xview_scroll(direction, "units")
            else:
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview_scroll(direction, "units")
            return
    _old_mouse_wheel_all(self, event)
ctk.CTkScrollableFrame._mouse_wheel_all = _patched_mouse_wheel_all

_old_init = ctk.CTkScrollableFrame.__init__
def _patched_init(self, *args, **kwargs):
    _old_init(self, *args, **kwargs)
    if sys.platform.startswith("linux"):
        self.bind_all("<MouseWheel>", self._mouse_wheel_all, add="+")
ctk.CTkScrollableFrame.__init__ = _patched_init


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GIU CMS Downloader")
        self.geometry("800x500")

        self.update_queue = queue.Queue()
        self.worker = None

        self.cached_courses = None

        env_path = get_app_dir() / ".env"

        if env_path.exists():
            self.build_main_layout()
        else:
            self.build_login_only()

    def build_login_only(self):
        from ui.pages.login_page import LoginPage
        self.login_frame = LoginPage(self, on_success=self._on_setup_complete)
        self.login_frame.pack(fill="both", expand=True)

    def _on_setup_complete(self, courses=None):
        self.cached_courses = courses
        self.login_frame.destroy()
        self.build_main_layout()

    def build_main_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=140)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.sidebar_sep = ctk.CTkFrame(self, width=2, fg_color=("gray85", "gray16"))
        self.sidebar_sep.grid(row=0, column=0, sticky="nse", padx=(0, 0))

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew")

        self.run_bar_sep = ctk.CTkFrame(self, height=2, fg_color=("gray85", "gray16"))
        self.run_bar_sep.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.run_bar = ctk.CTkFrame(self, height=70, fg_color="transparent")
        self.run_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self._build_run_bar()

        for name in ("Courses", "Templates", "Blocking", "Schedule"):
            btn = ctk.CTkButton(self.sidebar, text=name, command=lambda n=name: self.show_page(n), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray80", "gray26"), anchor="w")
            btn.pack(fill="x", padx=10, pady=5)

        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="y", expand=True)

        self.login_btn = ctk.CTkButton(self.sidebar, text="Update Login", command=self.open_login, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray80", "gray26"), anchor="w")
        self.login_btn.pack(fill="x", padx=10, pady=10, side="bottom")

        self.show_page("Courses")

    def open_login(self):
        if self.worker and self.worker.is_alive():
            return
            
        for attr in ['sidebar', 'sidebar_sep', 'content', 'run_bar_sep', 'run_bar']:
            if hasattr(self, attr) and getattr(self, attr):
                getattr(self, attr).destroy()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.build_login_only()

    def _build_run_bar(self):
        self.run_button = ctk.CTkButton(self.run_bar, text="Run Now", command=self.start_run)
        self.run_button.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.run_bar, text="", anchor="w")
        self.status_label.grid(row=0, column=1, sticky="w", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.run_bar, width=300, mode="determinate")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=1, sticky="w", padx=10)
        self.progress_bar.grid_remove()

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
        elif name == "Schedule":
            from ui.pages.schedule_page import SchedulePage
            SchedulePage(self.content).pack(fill="both", expand=True)


    def start_run(self):
        self.run_button.configure(state="disabled")
        if hasattr(self, "login_btn"):
            self.login_btn.configure(state="disabled")
        self.status_label.configure(text="Starting...")
        
        from ui.worker import DownloadWorker
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

        if (self.worker and self.worker.is_alive()) or not self.update_queue.empty():
            self.after(100, self.poll_queue)

    def _handle_message(self, message):
        kind = message[0]

        if kind == "status":
            self.status_label.configure(text=message[1])

        elif kind == "log":
            self.status_label.configure(text=message[1])

        elif kind == "scan_done":
            self.status_label.configure(text=f"Found {message[1]} files")

        elif kind == "file_start":
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            title, done, total = message[1], message[2], message[3]
            self.status_label.configure(text=f"Downloading: {title} ({done}/{total})")
            self.progress_bar.grid()
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
                if self.progress_bar.cget("mode") != "indeterminate":
                    self.progress_bar.configure(mode="indeterminate")
                    self.progress_bar.start()

        elif kind in ("file_done", "file_skipped", "file_blocked", "file_failed"):
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(1)

        elif kind == "run_complete":
            self.progress_bar.stop()
            self.status_label.configure(text="Done")
            self.progress_bar.grid_remove()
            self.size_label.configure(text="")
            self.run_button.configure(state="normal")
            if hasattr(self, "login_btn"):
                self.login_btn.configure(state="normal")

        elif kind == "fatal_error":
            self.progress_bar.stop()
            self.status_label.configure(text=f"Error: {message[1]}")
            self.progress_bar.grid_remove()
            self.run_button.configure(state="normal")
            if hasattr(self, "login_btn"):
                self.login_btn.configure(state="normal")