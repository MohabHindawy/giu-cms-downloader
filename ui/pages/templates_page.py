import customtkinter as ctk
from tkinter import messagebox

from core.templates import load_templates, save_templates, StructureTemplate, DEFAULT_TEMPLATE_NAME


class ItemTypeTag(ctk.CTkFrame):
    def __init__(self, master, text: str, on_remove):
        super().__init__(master, fg_color=("gray80", "gray30"), corner_radius=6)
        self.text = text

        label = ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=12))
        label.pack(side="left", padx=(8, 4), pady=4)

        remove_btn = ctk.CTkButton(
            self, text="×", width=20, height=20,
            font=ctk.CTkFont(size=14), fg_color="transparent",
            hover_color=("gray70", "gray40"),
            command=lambda: on_remove(self),
        )
        remove_btn.pack(side="left", padx=(0, 4), pady=4)


class GroupCard(ctk.CTkFrame):
    def __init__(self, master, group_name: str, item_types: list[str], on_delete_group):
        super().__init__(master, fg_color=("gray90", "gray20"), corner_radius=8)
        self.group_name = group_name
        self.item_tags: list[ItemTypeTag] = []

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 4))

        self.name_entry = ctk.CTkEntry(header, width=180)
        self.name_entry.insert(0, group_name)
        self.name_entry.pack(side="left")

        delete_btn = ctk.CTkButton(
            header, text="Delete Group", width=100,
            fg_color="#e5484d", hover_color="#c13639",
            command=lambda: on_delete_group(self),
        )
        delete_btn.pack(side="right")

        self.tags_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tags_frame.pack(fill="x", padx=10, pady=(0, 6))

        for t in item_types:
            self._add_tag(t)

        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.new_type_entry = ctk.CTkEntry(add_frame, width=180, placeholder_text="New item type...")
        self.new_type_entry.pack(side="left")

        add_btn = ctk.CTkButton(add_frame, text="Add", width=50, command=self._add_item_type)
        add_btn.pack(side="left", padx=(6, 0))

    def _add_tag(self, text: str):
        tag = ItemTypeTag(self.tags_frame, text, on_remove=self._remove_tag)
        tag.pack(side="left", padx=(0, 6), pady=4)
        self.item_tags.append(tag)

    def _remove_tag(self, tag: ItemTypeTag):
        self.item_tags.remove(tag)
        tag.destroy()

    def _add_item_type(self):
        text = self.new_type_entry.get().strip()
        if not text:
            return
        existing = [t.text for t in self.item_tags]
        if text in existing:
            return
        self._add_tag(text)
        self.new_type_entry.delete(0, "end")

    def get_data(self) -> tuple[str, list[str]]:
        name = self.name_entry.get().strip() or self.group_name
        types = [t.text for t in self.item_tags]
        return name, types


class TemplatesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.templates = load_templates()
        self.group_cards: list[GroupCard] = []

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(top_bar, text="Template:").pack(side="left", padx=(0, 6))

        template_names = list(self.templates.keys())
        self.template_menu = ctk.CTkOptionMenu(
            top_bar, values=template_names,
            command=self._on_template_selected,
        )
        self.template_menu.set(template_names[0] if template_names else DEFAULT_TEMPLATE_NAME)
        self.template_menu.pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=10, pady=(0, 10))

        add_group_btn = ctk.CTkButton(bottom_bar, text="Add Group", width=100, command=self._add_group)
        add_group_btn.pack(side="left")

        save_btn = ctk.CTkButton(bottom_bar, text="Save Changes", command=self._save)
        save_btn.pack(side="right")

        self._load_template(self.template_menu.get())

    def _on_template_selected(self, name: str):
        self._load_template(name)

    def _load_template(self, name: str):
        for card in self.group_cards:
            card.destroy()
        self.group_cards.clear()

        template = self.templates.get(name)
        if template is None:
            return

        for group_name, item_types in template.groups.items():
            self._add_group_card(group_name, item_types)

    def _add_group_card(self, group_name: str, item_types: list[str]):
        card = GroupCard(self.scroll_frame, group_name, item_types, on_delete_group=self._delete_group)
        card.pack(fill="x", pady=6, padx=4)
        self.group_cards.append(card)

    def _add_group(self):
        self._add_group_card("New Group", [])

    def _delete_group(self, card: GroupCard):
        self.group_cards.remove(card)
        card.destroy()

    def _save(self):
        current_name = self.template_menu.get()

        groups = {}
        for card in self.group_cards:
            name, types = card.get_data()
            if name in groups:
                messagebox.showwarning("Duplicate Group", f"Group \"{name}\" appears more than once. Rename one before saving.")
                return
            groups[name] = types

        self.templates[current_name] = StructureTemplate(name=current_name, groups=groups)
        save_templates(self.templates)
