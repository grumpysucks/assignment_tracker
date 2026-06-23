from gui import *
from assignment import Assignment, AssignmentStorage
from tkinter import ttk, messagebox
import json
json_file = "../data/data.json"


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

if __name__ == "__main__":
    app = App()
    try:
        app.mainloop()
        app.save_data()
        print("Exited properly, saving data.")
    except KeyboardInterrupt:
        app.save_data()
        print("Keyboard interrupt, saving data.")
