import datetime
import json
import math
from assignment import Assignment
import time
json_data = '../data/data.json'

def process_data():
    try:
        with open(json_data, 'r') as f:
            data = json.load(f)
            if data:
                for key in data:
                    a = Assignment(key['name'], key['due_date'], key['priority'])
                    a.status = key['status']
                    a.time_status = key['time_status']
                    assignments.append(a)
            return True
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass

def save_data():
    with open(json_data, 'w') as f:
        json.dump([a.__dict__ for a in assignments] if assignments else [], f, indent = 2)


def view_assignments(student_assignments):
    a = "=== Your Assignments ===\n"
    for assignment in student_assignments:
        a += f"{assignment}\n"
    return a

def sort_assignments(student_assignments):
    if len(student_assignments) <= 1:
        return student_assignments
    right = []
    middle = []
    left = []
    for assignment in student_assignments:
        if assignment.priority == 'high':
            left.append(assignment)
        elif assignment.priority == 'medium':
            middle.append(assignment)
        else:
            right.append(assignment)
    student_assignments = []
    student_assignments.extend(left)
    student_assignments.extend(middle)
    student_assignments.extend(right)
    return student_assignments

assignments = []
process_data()

while True:
    current_date = datetime.date.today()
    print("1. Add Assignment\n2. View Assignments\n3. Mark Complete\n4. Statistics\n5. Clear Assignments\n6. Exit")
    try:
        choice = int(input("Enter your choice(1-5)-> "))
    except ValueError:
        print("Please enter a valid choice(number)")
    else:
        while choice not in [i+1 for i in range(6)]:
            try:
                choice = int(input("Please choose from (1-5)-> "))
            except ValueError:
                print("Please enter a valid choice(number)")
        if choice == 1:
            name = input("Name->")
            due_date = input("Due Date(MM/DD/YYYY)-> ")
            while len(due_date) != 10 or "/" not in due_date or not due_date.replace('/', '').isdigit():
                print("Length of date must be 10 characters include slashes and must be in number form")
                due_date = input("Due Date(MM/DD/YYYY)-> ")
            due_date = datetime.datetime.strptime(due_date, "%m/%d/%Y").date()
            while due_date < current_date:
                print("Warning! This assignment is already past due date!")
                answer = input("Are you sure you would like to add assignment?(y/n)-> ")
                while answer.lower() not in ['y', 'yes','n', 'no']:
                    print("Please enter yes, y, n, or no")
                    answer = input("Are you sure you would like to add assignment?(y/n)-> ")
                if answer.lower() in ['y', 'yes']:
                    break
                else:
                    due_date = input("Due Date(MM/DD/YYYY)-> ")
                    while len(due_date) != 10 or "/" not in due_date or not due_date.replace('/', '').isdigit():
                        print("Length of date must be 10 characters include slashes and must be in number form")
                        due_date = input("Due Date(MM/DD/YYYY)-> ")
                    due_date = datetime.datetime.strptime(due_date, "%m/%d/%Y")
            due_date = datetime.datetime.strftime(due_date, "%m/%d/%Y")
            priority = input("Priority(low, medium, high)-> ")
            while priority.lower() not in ["low", "medium", "high"]:
                print("Priority must be low, medium, or high")
                priority = input("Priority(low, medium, high)-> ")
            assignments.append(Assignment(name, due_date, priority))
            print("Assignment added")
        elif choice == 2:
            sorted_assignments = sort_assignments(assignments)
            print(view_assignments(sorted_assignments))
        elif choice == 3:
            a = input("Assignment name-> ")
            for assignment in assignments:
                if assignment.name == a:
                    assignment.mark_completed()
                    break
            else:
                print('Assignment not found')
        elif choice == 4:
            completed = len([a for a in assignments if a.status])
            completion_rate = math.floor((completed / len(assignments)) * 100) if assignments else 0
            print(f"Total Assignments: {len(assignments)}\nCompleted: {completed}\nIncomplete: {len(assignments) - completed}\nCompletion Rate: {completion_rate}%")
        elif choice == 5:
            assignments = []
            save_data()
        elif choice == 6:
            print("Saving data...")
            print("Exiting...")
            save_data()
            break

