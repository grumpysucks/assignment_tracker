import datetime

class Assignment:
    def __init__(self, name, due_date, priority):
        current_date = datetime.datetime.today()
        due_date = datetime.datetime.strptime(due_date, "%m/%d/%Y")
        self.name = name
        self.due_date = datetime.datetime.strftime(due_date, "%m/%d/%Y")
        self.time_status = 'Due' if current_date < due_date else 'Past Due'
        self.status = False
        self.priority = priority

    def __str__(self):
        parsed_date = datetime.datetime.strptime(self.due_date, '%m/%d/%Y').strftime("%B %d") if self.time_status == "Due" else datetime.datetime.strptime(self.due_date, '%m/%d/%Y').strftime("%B %d, %Y")
        return f"Assignment: {self.name} | Due Date: {parsed_date} | Status: {'Completed' if self.status else 'Incomplete'} | Time Status: {self.time_status} | Priority: {self.priority}"

    def mark_completed(self):
        if self.status:
            print("Assignment already completed")
            return
        self.status = True
        print("Assignment completed")