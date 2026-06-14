import datetime
import json
import math
from assignment import Assignment
import time

starting_time = time.time()

def process_data():
    try:
        with open('../data/data.json', 'r') as f:
            data = json.load(f)
            for key in data:
                a = Assignment(key['name'], key['due_date'], key['priority'])
                a.status = key['status']
                a.time_status = key['time_status']
                assignments.append(a)
            return True
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass

def save_data():
    with open('../data/data.json', 'w') as f:
        json.dump([a.__dict__ for a in assignments], f)

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
    current_date = datetime.date.today().strftime("%m/%d/%Y")
    print("1. Add Assignment\n2. View Assignments\n3. Mark Complete\n4. Statistics\n5. Exit")
    try:
        choice = int(input("Enter your choice(1-5)-> "))
    except ValueError:
        print("Please enter a valid choice(number)")
    else:
        while choice not in [1,2,3,4,5]:
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
            print(f"Total Assignments: {len(assignments)}\nCompleted: {completed}\nIncomplete: {len(assignments) - completed}\nCompletion Rate: {math.floor((completed/len(assignments))*100)}%")
        elif choice == 5:
            print("Saving data...")
            print("Exiting...")
            save_data()
            break

print(time.time()-starting_time)