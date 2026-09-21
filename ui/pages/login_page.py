import customtkinter as ctk

from core.course_config import read_env, write_env
from paths import get_app_dir


class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container, text="GIU CMS Downloader",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(0, 20))

        env = read_env()

        ctk.CTkLabel(container, text="Username").pack(anchor="w", pady=(0, 4))
        self.username_entry = ctk.CTkEntry(container, width=300)
        self.username_entry.insert(0, env.get("GIU_USERNAME", ""))
        self.username_entry.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(container, text="Password").pack(anchor="w", pady=(0, 4))
        
        pw_frame = ctk.CTkFrame(container, fg_color="transparent")
        pw_frame.pack(fill="x", pady=(0, 12))
        
        self.password_entry = ctk.CTkEntry(pw_frame, show="•")
        self.password_entry.insert(0, env.get("GIU_PASSWORD", ""))
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        self.show_password = False
        self.eye_button = ctk.CTkButton(
            pw_frame, text="👁", width=36, command=self.toggle_password,
        )
        self.eye_button.pack(side="right")

        ctk.CTkLabel(container, text="Download folder (leave blank for default)").pack(anchor="w", pady=(0, 4))
        
        folder_frame = ctk.CTkFrame(container, fg_color="transparent")
        folder_frame.pack(fill="x", pady=(0, 4))
        
        self.folder_entry = ctk.CTkEntry(folder_frame)
        self.folder_entry.insert(0, env.get("DOWNLOAD_ROOT", ""))
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        browse_btn = ctk.CTkButton(folder_frame, text="Browse...", width=74, command=self.browse_folder)
        browse_btn.pack(side="right")

        from paths import get_app_dir
        if not (get_app_dir() / "state.json").exists():
            self.ignore_old_var = ctk.StringVar(value="0")
            self.ignore_old_checkbox = ctk.CTkCheckBox(
                container, text="Mark all existing files as already downloaded",
                variable=self.ignore_old_var, onvalue="1", offvalue="0"
            )
            self.ignore_old_checkbox.pack(pady=(10, 0), anchor="w")
        else:
            self.ignore_old_var = None

        self.error_label = ctk.CTkLabel(container, text="", text_color="#e5484d")
        self.error_label.pack(pady=(4, 0))

        self.continue_button = ctk.CTkButton(
            container, text="Continue", command=self.submit, width=300,
        )
        self.continue_button.pack(pady=(10, 0))

    def toggle_password(self):
        self.show_password = not self.show_password
        self.password_entry.configure(show="" if self.show_password else "•")
        self.eye_button.configure(text="🙈" if self.show_password else "👁")

    def browse_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory()
        if path:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, path)

    def submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        download_root = self.folder_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="Username and password are required.")
            return

        self.continue_button.configure(state="disabled", text="Checking...")
        self.error_label.configure(text="")
        self.update_idletasks()

        from core.auth import get_session
        from core.scraper import get_courses
        from core.config import BASE_URL

        try:
            session = get_session(username, password)
            courses = get_courses(session, BASE_URL)
        except Exception as e:
            self.error_label.configure(text=f"Login failed: {e}")
            self.continue_button.configure(state="normal", text="Continue")
            return

        env = read_env()
        env["GIU_USERNAME"] = username
        env["GIU_PASSWORD"] = password
        env["DOWNLOAD_ROOT"] = download_root
        
        if self.ignore_old_var and self.ignore_old_var.get() == "1":
            env["IGNORE_OLD_FILES"] = "1"
        else:
            env.pop("IGNORE_OLD_FILES", None)

        write_env(env)

        self.on_success(courses)