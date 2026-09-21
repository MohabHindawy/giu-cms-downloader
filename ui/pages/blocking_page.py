import customtkinter as ctk

from core.blocking import BlockingRule, load_rules, save_rules


class NameTag(ctk.CTkFrame):
    def __init__(self, master, text: str, on_remove):
        super().__init__(master, fg_color=("gray80", "gray30"), corner_radius=6)
        self.text = text

        label = ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=12))
        label.pack(side="left", padx=(8, 4), pady=4)

        remove_btn = ctk.CTkButton(
            self,
            text="×",
            width=20,
            height=20,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=("gray70", "gray40"),
            command=lambda: on_remove(self),
        )
        remove_btn.pack(side="left", padx=(0, 4), pady=4)


class BlockingPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.name_tags: list[NameTag] = []

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=(10, 2))

        ctk.CTkLabel(
            info_frame,
            text="Download Filters",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=(
                "Set rules to prevent certain files from downloading automatically.\n"
                "You can skip large files, or ignore files that match specific keywords."
            ),
            text_color=("gray40", "gray60"),
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        rules = load_rules()
        size_rule = None
        name_values = []
        for r in rules:
            if r.type == "size_over_mb" and size_rule is None:
                size_rule = r
            elif r.type == "name_contains":
                name_values.append(r.value)

        size_section = ctk.CTkFrame(
            self, fg_color=("gray90", "gray20"), corner_radius=8
        )
        size_section.pack(fill="x", padx=10, pady=(10, 6))

        size_header = ctk.CTkFrame(size_section, fg_color="transparent")
        size_header.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(
            size_header,
            text="Skip large files",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        self.size_enabled = ctk.CTkSwitch(
            size_header,
            text="Enable",
            width=50,
            command=self._on_size_toggle,
        )
        self.size_enabled.pack(side="right")
        if size_rule is not None:
            self.size_enabled.select()

        size_body = ctk.CTkFrame(size_section, fg_color="transparent")
        size_body.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(size_body, text="Skip files larger than").pack(side="left")

        self.size_entry = ctk.CTkEntry(size_body, width=70)
        self.size_entry.insert(0, size_rule.value if size_rule else "50")
        self.size_entry.pack(side="left", padx=6)
        self.size_entry.bind("<FocusOut>", lambda e: self._save())
        self.size_entry.bind("<Return>", lambda e: self._save())

        if self.size_enabled.get():
            self.size_entry.configure(state="normal", text_color=("gray10", "gray90"))
        else:
            self.size_entry.configure(state="disabled", text_color="gray50")

        ctk.CTkLabel(size_body, text="MB").pack(side="left")

        name_section = ctk.CTkFrame(
            self, fg_color=("gray90", "gray20"), corner_radius=8
        )
        name_section.pack(fill="x", padx=10, pady=(6, 10))

        name_header = ctk.CTkFrame(name_section, fg_color="transparent")
        name_header.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(
            name_header,
            text="Skip files by name",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left", anchor="w")

        ctk.CTkLabel(
            name_section,
            text="Files whose title contains any of these will be skipped",
            text_color=("gray40", "gray60"),
            justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 6))

        self.tags_frame = ctk.CTkFrame(name_section, fg_color="transparent", height=1)
        self.tags_frame.pack(fill="x", padx=10, pady=(0, 6))

        for v in name_values:
            self._add_tag(v)

        add_frame = ctk.CTkFrame(name_section, fg_color="transparent")
        add_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.name_entry = ctk.CTkEntry(
            add_frame, width=200, placeholder_text="e.g. exam, recording..."
        )
        self.name_entry.pack(side="left")
        self.name_entry.bind("<Return>", lambda e: self._add_name())

        add_btn = ctk.CTkButton(add_frame, text="Add", width=50, command=self._add_name)
        add_btn.pack(side="left", padx=(6, 0))

    def _on_size_toggle(self):
        if self.size_enabled.get():
            self.size_entry.configure(state="normal", text_color=("gray10", "gray90"))
        else:
            self.size_entry.configure(state="disabled", text_color="gray50")
        self._save()

    def _add_tag(self, text: str):
        tag = NameTag(self.tags_frame, text, on_remove=self._remove_tag)
        tag.pack(side="left", padx=(0, 6), pady=4)
        self.name_tags.append(tag)

    def _remove_tag(self, tag: NameTag):
        self.name_tags.remove(tag)
        tag.destroy()
        self._save()

    def _add_name(self):
        text = self.name_entry.get().strip()
        if not text:
            return
        existing = [t.text for t in self.name_tags]
        if text in existing:
            return
        self._add_tag(text)
        self.name_entry.delete(0, "end")
        self._save()

    def _save(self):
        rules = []

        if self.size_enabled.get():
            value = self.size_entry.get().strip()
            try:
                float(value)
                rules.append(BlockingRule(type="size_over_mb", value=value))
            except ValueError:
                pass

        for tag in self.name_tags:
            rules.append(BlockingRule(type="name_contains", value=tag.text))

        save_rules(rules)
