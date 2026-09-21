import sys
import customtkinter as ctk

from core.scheduling import is_task_installed, install_task, remove_task

class SchedulePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=(10, 2))

        ctk.CTkLabel(
            info_frame, text="Automatic Downloads",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=(
                "You can set up Windows Task Scheduler to run the app in the background\n"
                "every hour. It will silently download new files using your saved configuration."
            ),
            text_color=("gray40", "gray60"),
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        if sys.platform != "win32":
            ctk.CTkLabel(
                self, text="Automatic scheduling is only supported on Windows.",
                text_color="#e5484d",
            ).pack(pady=40)
            return

        self.status_card = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=8)
        self.status_card.pack(fill="x", padx=10, pady=20)

        self.status_label = ctk.CTkLabel(
            self.status_card, text="",
            font=ctk.CTkFont(size=14),
        )
        self.status_label.pack(pady=(20, 10))

        self.action_btn = ctk.CTkButton(self.status_card, text="", command=self.toggle_task, width=200)
        self.action_btn.pack(pady=(0, 20))

        self.error_label = ctk.CTkLabel(self, text="", text_color="#e5484d")
        self.error_label.pack(pady=10)

        self.refresh_status()

    def refresh_status(self):
        installed = is_task_installed()
        if installed:
            self.status_label.configure(text="Background downloads are currently ENABLED.")
            self.action_btn.configure(text="Disable Automatic Downloads", fg_color="#e5484d", hover_color="#c13639")
        else:
            self.status_label.configure(text="Background downloads are currently DISABLED.")
            self.action_btn.configure(text="Enable Automatic Downloads", fg_color=["#3a7ebf", "#1f538d"], hover_color=["#325882", "#14375e"])
        self.error_label.configure(text="")

    def toggle_task(self):
        self.error_label.configure(text="")
        installed = is_task_installed()
        if installed:
            err = remove_task()
        else:
            err = install_task()
            
        if err:
            self.error_label.configure(text=err)
        self.refresh_status()
