from datetime import date, datetime
import re

class Assignment:
    priorities = ["Low", "Medium", "High"]
    def __init__(self, name, due_date, priority, notes = '', subject = ''):
        self.name = name
        self.subject = subject
        self.due_date = due_date
        self.time_status = self.due_label()
        self.status = False
        self.priority = priority
        self.notes = notes

    def __str__(self):
        return f"Assignment: {self.name} | Due Date: {self.due_date} | Status: {'Done' if self.status else 'Todo'} | Time Status: {"⚠ OVERDUE" if self.time_status == 'Past Due' else self.time_status} | Priority: {self.priority}"

    def mark_completed(self):
        if self.status:
            print("Assignment already completed")
            return
        self.status = True
        print("Assignment completed")

    def days_until_due(self):
        try:
            due = datetime.strptime(self.due_date, "%m/%d/%Y").date()
            return (due - date.today()).days
        except ValueError:
            return 9999

    def due_label(self):
        days = self.days_until_due()
        if days < -1:
            return f"Overdue by {abs(days)}d"
        elif days == -1:
            return f"Due yesterday"
        elif days == 0:
            return "Due today"
        elif days == 1:
            return "Due tomorrow"
        else:
            return f"Due in {days}d"

class AssignmentStorage:
    def __init__(self):
        self.assignments = []

    def add(self, assignment: Assignment):
        self.assignments.append(assignment)

    def remove(self, assignment: Assignment):
        self.assignments.remove(assignment)

    def search(self, key):
        if not key.strip():
            return self.assignments[:]
        results = []
        for assignment in self.assignments:
            fields = [assignment.name, assignment.subject, assignment.due_date, assignment.priority, assignment.notes]
            if any(re.search(key, str(f), re.IGNORECASE) for f in fields):
                results.append(assignment)
        return results