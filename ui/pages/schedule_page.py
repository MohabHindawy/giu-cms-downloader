import sys
import customtkinter as ctk


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
                "You can configure the app to launch automatically when your computer starts.\n"
                "It will sit quietly in your system tray and fetch new files in the background."
            ),
            text_color=("gray40", "gray60"),
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        if sys.platform != "win32":
            ctk.CTkLabel(
                self, text="Automatic startup is only supported on Windows.",
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
        
        interval_frame = ctk.CTkFrame(self.status_card, fg_color="transparent")
        interval_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(interval_frame, text="Run every:").pack(side="left", padx=(0, 10))
        
        from core.course_config import read_env
        env = read_env()
        saved_interval = env.get("SCHEDULE_INTERVAL", "1 Hour")
        
        self.intervals = ["30 Minutes", "1 Hour", "2 Hours", "4 Hours", "12 Hours", "Daily"]
        self.interval_var = ctk.StringVar(value=saved_interval if saved_interval in self.intervals else "1 Hour")
        self.interval_menu = ctk.CTkOptionMenu(
            interval_frame, values=self.intervals, variable=self.interval_var, command=self.on_interval_change
        )
        self.interval_menu.pack(side="left")

        self.action_btn = ctk.CTkButton(self.status_card, text="", command=self.toggle_task, width=200)
        self.action_btn.pack(pady=(0, 20))

        self.error_label = ctk.CTkLabel(self, text="", text_color="#e5484d")
        self.error_label.pack(pady=10)

        self.refresh_status()

    def on_interval_change(self, choice: str):
        from core.course_config import read_env, write_env
        env = read_env()
        env["SCHEDULE_INTERVAL"] = choice
        write_env(env)
        
        
        app = self.winfo_toplevel()
        if hasattr(app, 'reset_schedule_timer'):
            app.reset_schedule_timer()
            
        self.error_label.configure(text="Schedule updated to " + choice, text_color="#10b981")

    def refresh_status(self):
        from core.startup import is_in_startup
        installed = is_in_startup()
        if installed:
            self.status_label.configure(text="Background downloads are currently ENABLED.")
            self.action_btn.configure(text="Disable Automatic Downloads", fg_color="#e5484d", hover_color="#c13639")
        else:
            self.status_label.configure(text="Background downloads are currently DISABLED.")
            self.action_btn.configure(text="Enable Automatic Downloads", fg_color=["#3a7ebf", "#1f538d"], hover_color=["#325882", "#14375e"])
            
    def toggle_task(self):
        from core.startup import is_in_startup, add_to_startup, remove_from_startup
        self.error_label.configure(text="", text_color="#e5484d")
        installed = is_in_startup()
        if installed:
            err = remove_from_startup()
        else:
            err = add_to_startup()
            
        if err:
            self.error_label.configure(text=err)
            
        
        app = self.winfo_toplevel()
        if hasattr(app, 'reset_schedule_timer'):
            app.reset_schedule_timer()
            
        self.refresh_status()
