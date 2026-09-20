import customtkinter as ctk

from core.blocking import load_rules, save_rules, BlockingRule


class RuleRow(ctk.CTkFrame):
    def __init__(self, master, rule: BlockingRule, on_delete):
        super().__init__(master, fg_color=("gray90", "gray20"), corner_radius=8)

        if rule.type == "size_over_mb":
            label_text = f"Skip files larger than {rule.value} MB"
        elif rule.type == "name_contains":
            label_text = f"Skip files whose title contains \"{rule.value}\""
        else:
            label_text = f"{rule.type}: {rule.value}"

        label = ctk.CTkLabel(self, text=label_text, anchor="w")
        label.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        delete_btn = ctk.CTkButton(
            self, text="Delete", width=70,
            fg_color="#e5484d", hover_color="#c13639",
            command=lambda: on_delete(self),
        )
        delete_btn.pack(side="right", padx=10, pady=10)

        self.rule = rule


class BlockingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.rule_rows: list[RuleRow] = []

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(10, 6))

        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(add_frame, text="Type:").pack(side="left", padx=(0, 4))

        self.type_menu = ctk.CTkOptionMenu(
            add_frame, values=["size_over_mb", "name_contains"], width=140,
        )
        self.type_menu.set("size_over_mb")
        self.type_menu.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(add_frame, text="Value:").pack(side="left", padx=(0, 4))

        self.value_entry = ctk.CTkEntry(add_frame, width=180, placeholder_text="e.g. 50 or exam")
        self.value_entry.pack(side="left", padx=(0, 8))

        add_btn = ctk.CTkButton(add_frame, text="Add Rule", width=80, command=self._add_rule)
        add_btn.pack(side="left")

        self._load_rules()

    def _load_rules(self):
        rules = load_rules()
        for rule in rules:
            self._add_row(rule)

    def _add_row(self, rule: BlockingRule):
        row = RuleRow(self.scroll_frame, rule, on_delete=self._delete_row)
        row.pack(fill="x", pady=4, padx=4)
        self.rule_rows.append(row)

    def _delete_row(self, row: RuleRow):
        self.rule_rows.remove(row)
        row.destroy()
        self._save()

    def _add_rule(self):
        rule_type = self.type_menu.get()
        value = self.value_entry.get().strip()
        if not value:
            return

        if rule_type == "size_over_mb":
            try:
                float(value)
            except ValueError:
                return

        rule = BlockingRule(type=rule_type, value=value)
        self._add_row(rule)
        self.value_entry.delete(0, "end")
        self._save()

    def _save(self):
        rules = [row.rule for row in self.rule_rows]
        save_rules(rules)
