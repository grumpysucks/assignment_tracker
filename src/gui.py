import tkinter as tk
from tkinter import ttk, messagebox
from assignment import Assignment
from datetime import date, datetime

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

        tk.Frame(self, bg=C[a.priority.lower()], width=4).pack(side="left", fill="y")

        self.check_var = tk.BooleanVar(value=a.status)
        tk.Checkbutton(
            self, variable=self.check_var,
            bg=C["surface"], activebackground=C["surface"],
            selectcolor=C["bg"],
            command=lambda: on_toggle(a, self.check_var.get()),
        ).pack(side="left", padx=(10, 4))

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