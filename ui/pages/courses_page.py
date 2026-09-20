import customtkinter as ctk
from tkinter import filedialog

from core.auth import get_session
from core.scraper import get_courses
from core.course_config import load_mapping, save_mapping, CourseConfig, read_env
from core.templates import load_templates, DEFAULT_TEMPLATE_NAME
from core.config import BASE_URL


class CourseRow(ctk.CTkFrame):
    def __init__(self, master, course, existing: CourseConfig | None, template_names: list[str], download_root: str):
        super().__init__(master, fg_color=("gray90", "gray20"), corner_radius=8)
        self.course = course

        header = ctk.CTkLabel(
            self, text=f"{course.code} — {course.name}",
            font=ctk.CTkFont(weight="bold"),
        )
        header.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 4))

        default_name = existing.display_name if existing else course.name
        default_folder = existing.folder if existing else f"{download_root}/{default_name}"
        default_template = existing.template_name if existing else DEFAULT_TEMPLATE_NAME

        ctk.CTkLabel(self, text="Folder name").grid(row=1, column=0, sticky="w", padx=10)
        self.name_entry = ctk.CTkEntry(self, width=200)
        self.name_entry.insert(0, default_name)
        self.name_entry.grid(row=1, column=1, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(self, text="Save to").grid(row=2, column=0, sticky="w", padx=10)
        self.folder_entry = ctk.CTkEntry(self, width=280)
        self.folder_entry.insert(0, default_folder)
        self.folder_entry.grid(row=2, column=1, sticky="w", padx=10, pady=4)

        browse_btn = ctk.CTkButton(self, text="...", width=30, command=self.browse)
        browse_btn.grid(row=2, column=2, sticky="w", padx=(0, 10))

        ctk.CTkLabel(self, text="Structure").grid(row=3, column=0, sticky="w", padx=10, pady=(0, 10))
        self.template_menu = ctk.CTkOptionMenu(self, values=template_names or [DEFAULT_TEMPLATE_NAME])
        self.template_menu.set(default_template)
        self.template_menu.grid(row=3, column=1, sticky="w", padx=10, pady=(0, 10))

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, path)

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
        try:
            session = get_session(env["GIU_USERNAME"], env["GIU_PASSWORD"])
            courses = get_courses(session, BASE_URL)
        except Exception as e:
            self.status_label.configure(text=f"Couldn't load courses: {e}")
            return

        self.status_label.destroy()

        mapping = load_mapping()
        templates = load_templates()
        template_names = list(templates.keys())
        download_root = env.get("DOWNLOAD_ROOT", "")

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        for course in courses:
            existing = mapping.get(course.code)
            row = CourseRow(self.scroll_frame, course, existing, template_names, download_root)
            row.pack(fill="x", pady=6, padx=4)
            self.rows.append(row)

        save_btn = ctk.CTkButton(self, text="Save Changes", command=self.save_all)
        save_btn.pack(pady=10)

    def save_all(self):
        mapping = load_mapping()
        for row in self.rows:
            mapping[row.course.code] = row.to_config()
        save_mapping(mapping)