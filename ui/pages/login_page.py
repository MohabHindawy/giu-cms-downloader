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
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        env = read_env()

        ctk.CTkLabel(container, text="Username").grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.username_entry = ctk.CTkEntry(container, width=260)
        self.username_entry.insert(0, env.get("GIU_USERNAME", ""))
        self.username_entry.grid(row=2, column=0, columnspan=2, pady=(0, 12))

        ctk.CTkLabel(container, text="Password").grid(row=3, column=0, sticky="w", pady=(0, 4))
        self.password_entry = ctk.CTkEntry(container, width=225, show="•")
        self.password_entry.insert(0, env.get("GIU_PASSWORD", ""))
        self.password_entry.grid(row=4, column=0, pady=(0, 12), sticky="w")

        self.show_password = False
        self.eye_button = ctk.CTkButton(
            container, text="👁", width=32, command=self.toggle_password,
        )
        self.eye_button.grid(row=4, column=1, padx=(6, 0), pady=(0, 12))

        ctk.CTkLabel(container, text="Download folder (leave blank for default)").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        self.folder_entry = ctk.CTkEntry(container, width=260)
        self.folder_entry.insert(0, env.get("DOWNLOAD_ROOT", ""))
        self.folder_entry.grid(row=6, column=0, columnspan=2, pady=(0, 4), sticky="w")

        browse_btn = ctk.CTkButton(container, text="Browse...", width=90, command=self.browse_folder)
        browse_btn.grid(row=6, column=1, sticky="e", pady=(0, 12))

        self.error_label = ctk.CTkLabel(container, text="", text_color="#e5484d")
        self.error_label.grid(row=7, column=0, columnspan=2)

        self.continue_button = ctk.CTkButton(
            container, text="Continue", command=self.submit, width=260,
        )
        self.continue_button.grid(row=8, column=0, columnspan=2, pady=(10, 0))

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
            get_courses(session, BASE_URL)
        except Exception as e:
            self.error_label.configure(text=f"Login failed: {e}")
            self.continue_button.configure(state="normal", text="Continue")
            return

        write_env({
            "GIU_USERNAME": username,
            "GIU_PASSWORD": password,
            "DOWNLOAD_ROOT": download_root,
        })

        self.on_success()