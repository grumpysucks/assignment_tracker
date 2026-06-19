import tkinter as tk
from datetime import date, datetime
from assignment import Assignment, AssignmentStorage
from tkinter import ttk, messagebox
import json
json_file = "../data/data.json"

C = {
    "bg":      "#0D1117",
    "surface": "#161B22",
    "border":  "#30363D",
    "accent":  "#58A6FF",
    "accent2": "#3FB950",
    "warn":    "#F85149",
    "amber":   "#E3B341",
    "text":    "#E6EDF3",
    "muted":   "#8B949E",
    "high":    "#F85149",
    "medium":  "#E3B341",
    "low":     "#3FB950",
}

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)


# ─── Custom Widgets ────────────────────────────────────────────────────────────

class StyledButton(tk.Button):
    def __init__(self, master, *args, variant="primary", **kwargs):
        colors = {
            "primary": {"bg": C["accent"],  "fg": C["bg"],    "abg": "#79BFFF"},
            "success": {"bg": C["accent2"], "fg": C["bg"],    "abg": "#5FD97A"},
            "danger":  {"bg": C["warn"],    "fg": C["text"],  "abg": "#FF7069"},
            "ghost":   {"bg": C["surface"], "fg": C["muted"], "abg": C["border"]},
        }
        c = colors.get(variant, colors["primary"])
        kwargs.setdefault("bg", c["bg"])
        kwargs.setdefault("fg", c["fg"])
        kwargs.setdefault("activebackground", c["abg"])
        kwargs.setdefault("activeforeground", kwargs["fg"])
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("padx", 14)
        kwargs.setdefault("pady", 7)
        kwargs.setdefault("font", FONT_BODY)
        kwargs.setdefault("cursor", "hand2")
        super().__init__(master, *args, **kwargs)


class StyledEntry(tk.Entry):
    def __init__(self, master, *args, **kwargs):
        kwargs.setdefault("bg", C["surface"])
        kwargs.setdefault("fg", C["text"])
        kwargs.setdefault("insertbackground", C["accent"])
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightcolor", C["accent"])
        kwargs.setdefault("highlightbackground", C["border"])
        kwargs.setdefault("font", FONT_BODY)
        super().__init__(master, *args, **kwargs)

    def set(self, value):
        self.delete(0, "end")
        self.insert(0, value)

class AssignmentPopUp(tk.Toplevel):
    def __init__(self, master, assignment_storage, assignment=None, on_save = None):
        super().__init__(master)
        self.storage = assignment_storage
        self.assignment = assignment
        self.title("Edit Assignment" if assignment else "New Assignment")
        self.configure(background=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self.on_save = on_save

    def _build(self):
        pad = {"padx": 20, "pady": 6}
        tk.Label(self, text="Assignment Name", bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", padx=20, pady=(20, 2))
        self.name_entry = StyledEntry(self, width=42)
        self.name_entry.pack(fill="x", **pad)

        tk.Label(self, text="Subject / Course", bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", padx=20, pady=(8, 2))
        self.subj_entry = StyledEntry(self, width=42)
        self.subj_entry.pack(fill="x", **pad)

        tk.Label(self, text="Due Date (DD/MM/YYYY)", bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", padx=20, pady=(8, 2))
        self.date_entry = StyledEntry(self, width=42)
        self.date_entry.pack(fill="x", **pad)
        self.date_entry.set(date.today().strftime("%m/%d/%Y"))

        tk.Label(self, text="Priority", bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", padx=20, pady=(8, 2))
        self.priority_var = tk.StringVar(value="Medium")
        pframe = tk.Frame(self, bg=C["bg"])
        pframe.pack(fill="x", padx=20, pady=6)
        for p in Assignment.priorities:
            tk.Radiobutton(
                pframe, text=p, variable=self.priority_var, value=p,
                bg=C["bg"], fg=C[p.lower()], selectcolor=C["surface"],
                activebackground=C["bg"], activeforeground=C[p.lower()],
                font=FONT_BODY,).pack(side="left", padx=(0, 16))

        tk.Label(self, text="Notes (optional)", bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", padx=20, pady=(8, 2))
        self.notes_text = tk.Text(
            self, width=40, height=3,
            bg=C["surface"], fg=C["text"], insertbackground=C["accent"],
            relief="flat", borderwidth=0, font=FONT_BODY,
            highlightthickness=1, highlightcolor=C["accent"],
            highlightbackground=C["border"],)
        self.notes_text.pack(fill="x", padx=20, pady=6)
        self.completed_var = tk.BooleanVar(value=False)
        if self.assignment:
            cf = tk.Frame(self, bg=C["bg"])
            cf.pack(anchor="w", padx=20, pady=4)
            tk.Checkbutton(
                cf, text="Mark as completed", variable=self.completed_var,
                bg=C["bg"], fg=C["text"], selectcolor=C["surface"],
                activebackground=C["bg"], font=FONT_BODY,
            ).pack(side="left")

        brow = tk.Frame(self, bg=C["bg"])
        brow.pack(fill="x", padx=20, pady=(12, 20))
        StyledButton(brow, text="Cancel", variant="ghost", command=self.destroy).pack(side="right", padx=(8, 0))
        StyledButton(brow, text="Save", variant="primary", command=self._save).pack(side="right")
        if self.assignment:
            self.name_entry.set(self.assignment.name)
            self.subj_entry.set(self.assignment.subject)
            self.date_entry.set(self.assignment.due_date)
            self.priority_var.set(self.assignment.priority)
            self.notes_text.insert("1.0", self.assignment.notes)
            self.completed_var.set(self.assignment.status)

    def _save(self):
        name = self.name_entry.get()
        subject = self.subj_entry.get()
        due_date = self.date_entry.get()
        priority = self.priority_var.get()
        notes = self.notes_text.get("1.0", "end").strip()

        if not name:
            messagebox.showerror("Missing Field", "Please enter a name.", parent=self)
            return
        if not subject:
            messagebox.showerror("Missing Field", "Please enter a subject.", parent=self)
            return
        if not due_date:
            messagebox.showerror("Missing Field", "Please enter a due date.", parent=self)
            return
        try:
            datetime.strptime(due_date, "%m/%d/%Y")
        except ValueError:
            messagebox.showerror("Missing Field", "Please enter a valid date (e.g. 01/01/2026).", parent=self)
            return
        if self.assignment:
            self.assignment.name = name
            self.assignment.subject = subject
            self.assignment.due_date = due_date
            self.assignment.priority = priority
            self.assignment.notes = notes
            self.assignment.status = self.completed_var.get()
        else:
            self.storage.add(Assignment(name, due_date, priority, notes = notes, subject=subject))

        if self.on_save:
            self.on_save()
        self.destroy()


class AssignmentCard(tk.Frame):
    def __init__(self, master, assignment, on_toggle, on_edit, on_delete):
        super().__init__(master, bg=C["surface"])
        self.assignment = assignment
        self._build(on_toggle, on_edit, on_delete)

    def _build(self, on_toggle, on_edit, on_delete):
        a = self.assignment
        days = a.days_until_due()

        # priority stripe
        tk.Frame(self, bg=C[a.priority.lower()], width=4).pack(side="left", fill="y")

        # checkbox
        self.check_var = tk.BooleanVar(value=a.status)
        tk.Checkbutton(
            self, variable=self.check_var,
            bg=C["surface"], activebackground=C["surface"],
            selectcolor=C["bg"],
            command=lambda: on_toggle(a, self.check_var.get()),
        ).pack(side="left", padx=(10, 4))

        # info
        info = tk.Frame(self, bg=C["surface"])
        info.pack(side="left", fill="both", expand=True, padx=4, pady=10)

        tk.Label(
            info, text=a.name, bg=C["surface"],
            fg=C["muted"] if a.status else C["text"],
            font=("Segoe UI", 11, "normal" if a.status else "bold"),
            anchor="w",
        ).pack(fill="x")

        tk.Label(info, text=a.subject, bg=C["surface"], fg=C["muted"],
                 font=FONT_SMALL, anchor="w").pack(fill="x")

        if a.notes:
            tk.Label(
                info, text=a.notes[:80] + ("…" if len(a.notes) > 80 else ""),
                bg=C["surface"], fg=C["muted"], font=FONT_SMALL, anchor="w",
            ).pack(fill="x")

        # right panel
        right = tk.Frame(self, bg=C["surface"])
        right.pack(side="right", padx=10, pady=8)

        if a.status:
            due_color = C["muted"]
        elif days < 0:
            due_color = C["warn"]
        elif days <= 3:
            due_color = C["amber"]
        else:
            due_color = C["accent2"]

        tk.Label(right, text=a.due_label(), bg=C["surface"], fg=due_color,
                 font=("Segoe UI", 9, "bold")).pack(anchor="e")
        tk.Label(right, text=a.priority, bg=C["surface"], fg=C[a.priority.lower()],
                 font=FONT_SMALL).pack(anchor="e", pady=(2, 6))

        btn_row = tk.Frame(right, bg=C["surface"])
        btn_row.pack(anchor="e")
        StyledButton(btn_row, text="Edit", variant="ghost", command=lambda: on_edit(a),
                     padx=8, pady=3, font=FONT_SMALL).pack(side="left", padx=(0, 4))
        StyledButton(btn_row, text="✕", variant="danger", command=lambda: on_delete(a),
                     padx=8, pady=3, font=FONT_SMALL).pack(side="left")

        tk.Frame(self, bg=C["border"], height=1).pack(side="bottom", fill="x")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assignment Tracker")
        self.geometry("820x680")
        self.minsize(640, 480)
        self.configure(bg=C["bg"])

        self.store = AssignmentStorage()
        self.sort_key = tk.StringVar(value="Due Date")
        self.sort_reverse = tk.BooleanVar(value=False)
        self.filter_status = tk.StringVar(value="All")
        self._search_query = ""

        self._load_data()
        self._build_ui()
        self.refresh()

    def _load_data(self):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                if data:
                    for key in data:
                        assignment = Assignment(key['name'], key['due_date'], key['priority'], key['notes'], key['subject'])
                        self.store.add(assignment)
                    return True
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Data not present")
            return None

    def save_data(self):
        with open(json_file, "w") as file:
            json.dump([a.__dict__ for a in self.store.assignments] if self.store.assignments else [], file, indent = 2)


    def _build_ui(self):
        # header
        header = tk.Frame(self, bg=C["bg"], pady=16)
        header.pack(fill="x", padx=24)
        tk.Label(header, text="📚 Assignment Tracker",
                 bg=C["bg"], fg=C["text"], font=FONT_TITLE).pack(side="left")
        StyledButton(header, text="+ New Assignment", variant="primary",
                     command=self._add_assignment).pack(side="right", pady=4)

        # toolbar
        toolbar = tk.Frame(self, bg=C["surface"], pady=10)
        toolbar.pack(fill="x", padx=24, pady=(0, 12))

        tk.Label(toolbar, text="🔍", bg=C["surface"], fg=C["muted"]).pack(side="left", padx=(12, 4))
        self.search_entry = StyledEntry(toolbar, width=24)
        self.search_entry.configure(bg=C["surface"])
        self.search_entry.pack(side="left", ipady=4)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        tk.Frame(toolbar, bg=C["border"], width=1).pack(side="left", fill="y", padx=12)

        tk.Label(toolbar, text="Sort:", bg=C["surface"], fg=C["muted"], font=FONT_SMALL).pack(side="left", padx=(0, 4))
        sort_menu = ttk.Combobox(toolbar, textvariable=self.sort_key,
                                 values=["Due Date", "Name", "Subject", "Priority", "Status"],
                                 width=10, state="readonly", font=FONT_SMALL)
        sort_menu.pack(side="left")
        sort_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        tk.Checkbutton(
            toolbar, text="Reverse", variable=self.sort_reverse,
            bg=C["surface"], fg=C["muted"], selectcolor=C["bg"],
            activebackground=C["surface"], font=FONT_SMALL, command=self.refresh,
        ).pack(side="left", padx=8)

        tk.Frame(toolbar, bg=C["border"], width=1).pack(side="left", fill="y", padx=12)

        tk.Label(toolbar, text="Show:", bg=C["surface"], fg=C["muted"], font=FONT_SMALL).pack(side="left", padx=(0, 4))
        for label in ["All", "Pending", "Completed"]:
            tk.Radiobutton(
                toolbar, text=label, variable=self.filter_status, value=label,
                bg=C["surface"], fg=C["text"], selectcolor=C["bg"],
                activebackground=C["surface"], font=FONT_SMALL, command=self.refresh,
            ).pack(side="left", padx=4)

        # stats
        self.stats_frame = tk.Frame(self, bg=C["bg"])
        self.stats_frame.pack(fill="x", padx=24, pady=(0, 8))

        # scrollable list
        container = tk.Frame(self, bg=C["bg"])
        container.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self._canvas = tk.Canvas(container, bg=C["bg"], highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self._canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._canvas.configure(yscrollcommand=scrollbar.set)

        self.list_frame = tk.Frame(self._canvas, bg=C["bg"])
        self._win = self._canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._win, width=e.width))
        self._canvas.bind_all("<MouseWheel>", lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=C["surface"], background=C["surface"],
                        foreground=C["text"], selectbackground=C["accent"],
                        bordercolor=C["border"], arrowcolor=C["muted"])
        style.configure("TScrollbar", background=C["border"],
                        troughcolor=C["bg"], bordercolor=C["bg"])

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        results = self.store.search(self._search_query)

        status = self.filter_status.get()
        if status == "Pending":
            results = [a for a in results if not a.status]
        elif status == "Completed":
            results = [a for a in results if a.status]

        sort_map = {
            "Name": lambda a: a.name.lower(),
            "Subject": lambda a: a.subject.lower(),
            "Due Date": lambda a: a.due_date,
            "Priority": lambda a: Assignment.priorities.index(a.priority),
            "Status": lambda a: (0 if not a.status else 1),
        }
        results.sort(key=sort_map.get(self.sort_key.get(), lambda a: a.due_date),
                     reverse=self.sort_reverse.get())

        self._render_stats()

        if not results:
            msg = "No assignments match your search." if self._search_query else "No assignments yet.\nClick '+ New Assignment' to get started."
            tk.Label(self.list_frame, text=msg, bg=C["bg"], fg=C["muted"],
                     font=("Segoe UI", 12), justify="center", pady=40).pack()
            return

        for a in results:
            AssignmentCard(
                self.list_frame, a,
                on_toggle=self._toggle_complete,
                on_edit=self._edit_assignment,
                on_delete=self._delete_assignment,
            ).pack(fill="x", pady=(0, 6))

    def _render_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        all_a = self.store.assignments
        total = len(all_a)
        done = sum(1 for a in all_a if a.status)
        overdue = sum(1 for a in all_a if not a.status and a.days_until_due() < 0)
        due_soon = sum(1 for a in all_a if not a.status and 0 <= a.days_until_due() <= 3)
        for val, label, color in [
            (str(total), "Total", C["text"]),
            (str(total - done), "Pending", C["accent"]),
            (str(done), "Done", C["accent2"]),
            (str(overdue), "Overdue", C["warn"]),
            (str(due_soon), "Due Soon", C["amber"]),
        ]:
            chip = tk.Frame(self.stats_frame, bg=C["surface"], padx=14, pady=6)
            chip.pack(side="left", padx=(0, 8))
            tk.Label(chip, text=val, bg=C["surface"], fg=color,
                     font=("Segoe UI", 16, "bold")).pack()
            tk.Label(chip, text=label, bg=C["surface"], fg=C["muted"],
                     font=FONT_SMALL).pack()

    def _on_search(self, event=None):
        self._search_query = self.search_entry.get().strip()
        self.refresh()

    def _add_assignment(self):
        AssignmentPopUp(self, self.store, on_save=self.refresh)

    def _edit_assignment(self, assignment: Assignment):
        AssignmentPopUp(self, self.store, assignment=assignment, on_save=self.refresh)

    def _delete_assignment(self, assignment: Assignment):
        if messagebox.askyesno("Delete", f"Delete '{assignment.name}'?", parent=self):
            self.store.remove(assignment)
            self.refresh()

    def _toggle_complete(self, assignment: Assignment, value: bool):
        assignment.status = value
        self.refresh()


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.save_data()
