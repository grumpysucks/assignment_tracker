import datetime

class Assignment:
    def __init__(self, name, due_date, priority):
        self.name = name
        self.due_date = due_date
        self.time_status = 'Due'
        self.status = False
        self.priority = priority

    def __str__(self):
        parsed_date = datetime.datetime.strptime(self.due_date, '%m/%d/%Y').strftime("%B %d")
        return f"Assignment: {self.name} | Due Date: {parsed_date} | Status: {'Completed' if self.status else 'Incomplete'} | Time Status: {self.time_status} | Priority: {self.priority}"

    def mark_completed(self):
        if self.status:
            print("Assignment already completed")
            return
        self.status = True
        print("Assignment completed")