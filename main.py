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

def view_assignments(student_assignments):
    a = "=== Your Assignments ===\n"
    for assignment in student_assignments:
        a += f"{assignment}\n"
    return a

assignments = []
while True:
    current_date = datetime.date.today().strftime("%m/%d/%Y")
    print("1. Add Assignment\n2. View Assignments\n3. Mark Complete\n4. Exit")
    try:
        choice = int(input("Enter your choice(1,2,3,4)-> "))
    except ValueError:
        print("Please enter a valid choice(number)")
    else:
        while choice not in [1,2,3,4]:
            try:
                choice = int(input("Please choose from (1,2,3,4)-> "))
            except ValueError:
                print("Please enter a valid choice(number)")
        if choice == 1:
            name = input("Name->")
            due_date = input("Due Date(MM/DD/YYYY)-> ")
            while len(due_date) != 10 or "/" not in due_date or not due_date.replace('/', '').isdigit():
                print("Length of date must be 10 characters include slashes and must be in number form")
                due_date = input("Due Date(MM/DD/YYYY)-> ")
            priority = input("Priority(low, medium, high)-> ")
            while priority.lower() not in ["low", "medium", "high"]:
                print("Priority must be low, medium, or high")
                priority = input("Priority(low, medium, high)-> ")
            assignments.append(Assignment(name, due_date, priority))
            print("Assignment added")
        elif choice == 2:
            print(view_assignments(assignments))
        elif choice == 3:
            a = input("Assignment name-> ")
            for assignment in assignments:
                if assignment.name == a:
                    assignment.mark_completed()
                    break
            else:
                print('Assignment not found')
        elif choice == 4:
            break





