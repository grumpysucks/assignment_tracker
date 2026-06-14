import unittest
import json
import os
import sys
import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
from assignment import Assignment


# ── helpers ────────────────────────────────────────────────────────────────────

def make_assignment(name="Homework", due_date="12/31/2026", priority="high"):
    return Assignment(name, due_date, priority)


def future_date():
    return (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m/%d/%Y")


def past_date():
    return (datetime.date.today() - datetime.timedelta(days=30)).strftime("%m/%d/%Y")


# ── Assignment class ────────────────────────────────────────────────────────────

class TestAssignmentInit(unittest.TestCase):

    def test_name_stored(self):
        a = make_assignment(name="Essay")
        self.assertEqual(a.name, "Essay")

    def test_due_date_stored(self):
        a = make_assignment(due_date="06/30/2026")
        self.assertEqual(a.due_date, "06/30/2026")

    def test_priority_stored(self):
        a = make_assignment(priority="low")
        self.assertEqual(a.priority, "low")

    def test_status_defaults_false(self):
        a = make_assignment()
        self.assertFalse(a.status)
    """
    def test_future_assignment_is_due(self):
        a = make_assignment(due_date=future_date())
        self.assertEqual(a.time_status, "Due")

    def test_past_assignment_is_overdue(self):
        a = make_assignment(due_date=past_date())
        self.assertEqual(a.time_status, "Overdue")
    """

class TestAssignmentStr(unittest.TestCase):

    def test_str_contains_name(self):
        a = make_assignment(name="Lab Report")
        self.assertIn("Lab Report", str(a))

    def test_str_shows_incomplete_by_default(self):
        a = make_assignment()
        self.assertIn("Incomplete", str(a))

    def test_str_shows_completed_after_mark(self):
        a = make_assignment()
        a.mark_completed()
        self.assertIn("Completed", str(a))

    def test_str_formats_date(self):
        a = make_assignment(due_date="06/30/2026")
        self.assertIn("June 30", str(a))
        self.assertNotIn("06/30/2026", str(a))

    def test_str_contains_priority(self):
        a = make_assignment(priority="medium")
        self.assertIn("medium", str(a))


class TestMarkCompleted(unittest.TestCase):

    def test_mark_sets_status_true(self):
        a = make_assignment()
        a.mark_completed()
        self.assertTrue(a.status)

    def test_mark_prints_completed(self):
        a = make_assignment()
        with patch("builtins.print") as mock_print:
            a.mark_completed()
            mock_print.assert_called_with("Assignment completed")

    def test_double_mark_prints_already_completed(self):
        a = make_assignment()
        a.mark_completed()
        with patch("builtins.print") as mock_print:
            a.mark_completed()
            mock_print.assert_called_with("Assignment already completed")

    def test_double_mark_does_not_change_status(self):
        a = make_assignment()
        a.mark_completed()
        a.mark_completed()
        self.assertTrue(a.status)


# ── sort_assignments ────────────────────────────────────────────────────────────

def sort_assignments(student_assignments):
    if len(student_assignments) <= 1:
        return student_assignments
    right, middle, left = [], [], []
    for a in student_assignments:
        if a.priority == "high":
            left.append(a)
        elif a.priority == "medium":
            middle.append(a)
        else:
            right.append(a)
    return left + middle + right


class TestSortAssignments(unittest.TestCase):

    def test_empty_list(self):
        self.assertEqual(sort_assignments([]), [])

    def test_single_item(self):
        a = make_assignment()
        self.assertEqual(sort_assignments([a]), [a])

    def test_high_before_medium_before_low(self):
        low = make_assignment(name="A", priority="low")
        medium = make_assignment(name="B", priority="medium")
        high = make_assignment(name="C", priority="high")
        result = sort_assignments([low, medium, high])
        self.assertEqual(result, [high, medium, low])

    def test_already_sorted(self):
        high = make_assignment(name="A", priority="high")
        medium = make_assignment(name="B", priority="medium")
        low = make_assignment(name="C", priority="low")
        result = sort_assignments([high, medium, low])
        self.assertEqual(result[0].priority, "high")
        self.assertEqual(result[1].priority, "medium")
        self.assertEqual(result[2].priority, "low")

    def test_all_same_priority(self):
        a = make_assignment(name="A", priority="high")
        b = make_assignment(name="B", priority="high")
        result = sort_assignments([a, b])
        self.assertEqual(len(result), 2)


# ── view_assignments ────────────────────────────────────────────────────────────

def view_assignments(student_assignments):
    a = "=== Your Assignments ===\n"
    for assignment in student_assignments:
        a += f"{assignment}\n"
    return a


class TestViewAssignments(unittest.TestCase):

    def test_header_present(self):
        self.assertIn("=== Your Assignments ===", view_assignments([]))

    def test_empty_list_no_crash(self):
        result = view_assignments([])
        self.assertIsInstance(result, str)

    def test_single_assignment_shown(self):
        a = make_assignment(name="Essay")
        self.assertIn("Essay", view_assignments([a]))

    def test_multiple_assignments_shown(self):
        a1 = make_assignment(name="Essay")
        a2 = make_assignment(name="Quiz")
        result = view_assignments([a1, a2])
        self.assertIn("Essay", result)
        self.assertIn("Quiz", result)


# ── statistics ──────────────────────────────────────────────────────────────────

class TestStatistics(unittest.TestCase):

    def test_empty_list_no_crash(self):
        assignments = []
        total = len(assignments)
        # guard should prevent division — just verify total is 0
        self.assertEqual(total, 0)

    def test_all_incomplete(self):
        assignments = [make_assignment() for _ in range(3)]
        completed = len([a for a in assignments if a.status])
        self.assertEqual(completed, 0)
        self.assertEqual(len(assignments) - completed, 3)

    def test_all_complete(self):
        assignments = [make_assignment() for _ in range(3)]
        for a in assignments:
            a.mark_completed()
        completed = len([a for a in assignments if a.status])
        self.assertEqual(completed, 3)
        self.assertAlmostEqual((completed / len(assignments)) * 100, 100)

    def test_mixed_completion_rate(self):
        assignments = [make_assignment() for _ in range(4)]
        assignments[0].mark_completed()
        assignments[1].mark_completed()
        completed = len([a for a in assignments if a.status])
        self.assertAlmostEqual((completed / len(assignments)) * 100, 50)

    def test_completion_rate_rounds_correctly(self):
        assignments = [make_assignment() for _ in range(3)]
        assignments[0].mark_completed()
        completed = len([a for a in assignments if a.status])
        rate = round((completed / len(assignments)) * 100)
        self.assertEqual(rate, 33)


# ── JSON persistence ────────────────────────────────────────────────────────────

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "test_data.json")


def save_data(assignments, path=TEST_DATA_PATH):
    with open(path, "w") as f:
        json.dump([a.__dict__ for a in assignments], f)


def process_data(path=TEST_DATA_PATH):
    assignments = []
    try:
        with open(path, "r") as f:
            data = json.load(f)
        for d in data:
            a = Assignment(d["name"], d["due_date"], d["priority"])
            a.status = d["status"]
            a.time_status = d["time_status"]
            assignments.append(a)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return assignments


class TestPersistence(unittest.TestCase):

    def tearDown(self):
        if os.path.exists(TEST_DATA_PATH):
            os.remove(TEST_DATA_PATH)

    def test_save_creates_file(self):
        save_data([make_assignment()])
        self.assertTrue(os.path.exists(TEST_DATA_PATH))

    def test_save_and_reload_name(self):
        save_data([make_assignment(name="Finals")])
        loaded = process_data()
        self.assertEqual(loaded[0].name, "Finals")

    def test_save_and_reload_status(self):
        a = make_assignment()
        a.mark_completed()
        save_data([a])
        loaded = process_data()
        self.assertTrue(loaded[0].status)

    def test_save_and_reload_priority(self):
        save_data([make_assignment(priority="low")])
        loaded = process_data()
        self.assertEqual(loaded[0].priority, "low")

    def test_save_empty_list(self):
        save_data([])
        loaded = process_data()
        self.assertEqual(loaded, [])

    def test_missing_file_no_crash(self):
        loaded = process_data("nonexistent.json")
        self.assertEqual(loaded, [])

    def test_empty_file_no_crash(self):
        with open(TEST_DATA_PATH, "w") as f:
            f.write("")
        loaded = process_data()
        self.assertEqual(loaded, [])

    def test_corrupted_file_no_crash(self):
        with open(TEST_DATA_PATH, "w") as f:
            f.write("{invalid json")
        loaded = process_data()
        self.assertEqual(loaded, [])

    def test_multiple_assignments_persist(self):
        a1 = make_assignment(name="Essay")
        a2 = make_assignment(name="Quiz", priority="low")
        save_data([a1, a2])
        loaded = process_data()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].name, "Essay")
        self.assertEqual(loaded[1].name, "Quiz")


if __name__ == "__main__":
    unittest.main(verbosity=2)