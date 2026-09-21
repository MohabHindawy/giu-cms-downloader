from tkinter import filedialog

import customtkinter as ctk

from core.auth import get_session
from core.config import BASE_URL
from core.course_config import CourseConfig, load_mapping, read_env, save_mapping
from core.scraper import get_courses
from core.templates import DEFAULT_TEMPLATE_NAME, load_templates


class CourseRow(ctk.CTkFrame):
    def __init__(
        self,
        master,
        course,
        existing: CourseConfig | None,
        template_names: list[str],
        download_root: str,
    ):
        super().__init__(master, fg_color=("gray90", "gray20"), corner_radius=8)
        self.course = course

        header = ctk.CTkLabel(
            self,
            text=f"{course.code} — {course.name}",
            font=ctk.CTkFont(weight="bold"),
        )
        header.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 4))

        default_name = existing.display_name if existing else course.name
        default_folder = (
            existing.folder if existing else f"{download_root}/{default_name}"
        )
        default_template = existing.template_name if existing else DEFAULT_TEMPLATE_NAME

        ctk.CTkLabel(self, text="Folder name").grid(
            row=1, column=0, sticky="w", padx=10
        )
        self.download_root = download_root
        self.manual_folder_edited = existing is not None

        self.name_var = ctk.StringVar(value=default_name)
        self.name_entry = ctk.CTkEntry(self, width=200, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=1, sticky="w", padx=10, pady=4)
        self.name_var.trace_add("write", self._on_name_change)

        ctk.CTkLabel(self, text="Save to").grid(row=2, column=0, sticky="w", padx=10)
        self.folder_var = ctk.StringVar(value=default_folder)
        self.folder_entry = ctk.CTkEntry(self, width=280, textvariable=self.folder_var)
        self.folder_entry.grid(row=2, column=1, sticky="w", padx=10, pady=4)
        self.folder_entry.bind("<Key>", self._on_manual_folder_edit)

        browse_btn = ctk.CTkButton(self, text="...", width=30, command=self.browse)
        browse_btn.grid(row=2, column=2, sticky="w", padx=(0, 10))

        ctk.CTkLabel(self, text="Structure").grid(
            row=3, column=0, sticky="w", padx=10, pady=(0, 10)
        )
        self.template_menu = ctk.CTkOptionMenu(
            self, values=template_names or [DEFAULT_TEMPLATE_NAME]
        )
        self.template_menu.set(default_template)
        self.template_menu.grid(row=3, column=1, sticky="w", padx=10, pady=(0, 10))

    def _on_manual_folder_edit(self, event):
        self.manual_folder_edited = True

    def _on_name_change(self, *args):
        if not self.manual_folder_edited:
            new_name = self.name_var.get().strip()
            self.folder_var.set(f"{self.download_root}/{new_name}")

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_var.set(path)
            self.manual_folder_edited = True

    def to_config(self) -> CourseConfig:
        return CourseConfig(
            display_name=self.name_entry.get().strip(),
            folder=self.folder_entry.get().strip(),
            template_name=self.template_menu.get(),
        )


class CoursesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.status_label = ctk.CTkLabel(self, text="Loading courses...")
        self.status_label.pack(pady=20)

        self.rows: list[CourseRow] = []
        self.scroll_frame = None

        self.after(50, self.load_courses)

    def load_courses(self):
        env = read_env()
        master = self.winfo_toplevel()

        courses = getattr(master, "cached_courses", None)
        if courses is not None:
            master.cached_courses = None
        else:
            try:
                session = get_session(env["GIU_USERNAME"], env["GIU_PASSWORD"])
                courses = get_courses(session, BASE_URL)
            except Exception as e:
                self.status_label.configure(
                    text=f"Couldn't load courses: {e}\n\nDid your password change?"
                )

                retry_btn = ctk.CTkButton(
                    self,
                    text="Update Login",
                    command=lambda: self.winfo_toplevel().open_login(),
                )
                retry_btn.pack(pady=10)
                return

        self.status_label.destroy()

        mapping = load_mapping()
        templates = load_templates()
        template_names = list(templates.keys())
        if "Flat" not in template_names:
            template_names.append("Flat")

        from pathlib import Path

        download_root = env.get("DOWNLOAD_ROOT", "").strip()
        if not download_root:
            download_root = str(Path.home() / "Downloads" / "GIU")

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=(10, 2))

        ctk.CTkLabel(
            info_frame,
            text="Course Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=(
                "Configure how each course is saved. Choose a folder location, and select\n"
                "a structure template to automatically organize downloads into subfolders.\n"
                "Select 'Flat' to have all files in one folder, select Structured to have\n"
                "files sorted into the subfolders style designed in the Structure page."
            ),
            text_color=("gray40", "gray60"),
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        for course in courses:
            existing = mapping.get(course.code)
            row = CourseRow(
                self.scroll_frame, course, existing, template_names, download_root
            )
            row.pack(fill="x", pady=6, padx=4)
            self.rows.append(row)

        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=10, pady=(0, 10))

        save_btn = ctk.CTkButton(bottom_bar, text="Save Changes", command=self.save_all)
        save_btn.pack(side="right")

    def save_all(self):
        mapping = load_mapping()
        for row in self.rows:
            cfg = row.to_config()
            if not cfg.folder:
                from tkinter import messagebox

                messagebox.showerror(
                    "Invalid Folder",
                    f"The destination folder for {row.course.name} cannot be blank.\n\nPlease choose a valid path before saving.",
                )
                return
            mapping[row.course.code] = cfg
        save_mapping(mapping)
        from tkinter import messagebox

        messagebox.showinfo("Saved", "Course configuration saved successfully!")
