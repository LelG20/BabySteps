"""
methods.py
Stand-alone functions: loading the CSV file and one demonstration function per
assignment task. Each demo prints a labelled section so the marker can follow
the program from Task 1 to Task 7.
"""
import csv

from classes import (
    REQUIRED_COLUMNS,
    SUBJECTS,
    AIUStudent,
    ScholarshipStudent,
    Student,
)


# ==========================================================================
# Task 1: loading the CSV dataset
# ==========================================================================
def load_students_from_csv(file_path):
    """
    Read students from a CSV file and return a list of Student objects.
    Rows with a ScholarshipAmount become ScholarshipStudent objects; the rest
    become AIUStudent objects. Invalid rows are skipped with a warning.
    """
    students = []
    with open(file_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV file is missing required columns: {', '.join(missing)}")

        for line_number, row in enumerate(reader, start=2):  # line 1 is the header
            try:
                marks = {subject: float(row[subject]) for subject in SUBJECTS}
                amount_text = (row.get("ScholarshipAmount") or "").strip()
                details = (row["StudentID"], row["FName"], row["LName"], row["Programme"], marks)
                if amount_text:
                    students.append(ScholarshipStudent(*details, float(amount_text)))
                else:
                    students.append(AIUStudent(*details))
            except (ValueError, TypeError, KeyError) as error:
                print(f"Warning: skipped CSV line {line_number}: {error}")
    return students


# ==========================================================================
# Demonstrations (Tasks 1 to 7)
# ==========================================================================
def print_heading(title):
    """Print a clear banner for each task."""
    print("\n" + "#" * 64)
    print(f"# {title}")
    print("#" * 64)


def demo_loading(students):
    """Task 1: show the students loaded from the CSV file."""
    print_heading("TASK 1 - Loading students from students.csv")
    print(f"Loaded {len(students)} students.")
    for student in students:
        print(f"  {student}  [{type(student).__name__}]")


def demo_abstraction_and_encapsulation():
    """Task 2: abstract class cannot be created; data is protected."""
    print_heading("TASK 2 - Abstraction and encapsulation")
    try:
        Student("00/000", "Test", "User", "MDS", {"Math": 50, "English": 50, "Science": 50})
    except TypeError as error:
        print(f"Abstraction: Student cannot be created directly -> {error}")

    demo = AIUStudent("00/001", "Demo", "Student", "MDS", {"Math": 70, "English": 70, "Science": 70})
    print(f"Read through a property : {demo.full_name}, average {demo.calculate_average():.2f}")
    demo.set_mark("Math", 90)
    print(f"After set_mark('Math', 90): average {demo.calculate_average():.2f}")
    for label, action in (
        ("set_mark('Math', 150)", lambda: demo.set_mark("Math", 150)),
        ("student_id = 'X'", lambda: setattr(demo, "student_id", "X")),
    ):
        try:
            action()
        except (ValueError, AttributeError) as error:
            print(f"Blocked {label:<22}: {error}")
    demo.get_marks()["Science"] = 0  # changes only a copy
    print(f"Changing the copy from get_marks() does not affect the student: {demo.get_marks()}")


def demo_analyzer_and_inheritance(students, analyzer):
    """Tasks 3 and 4: analyzer results, inheritance chain and overriding."""
    print_heading("TASKS 3 and 4 - PerformanceAnalyzer, inheritance and overriding")
    print(f"Highest average : {analyzer.highest_average()}")
    print(f"Lowest average  : {analyzer.lowest_average()}")
    print(f"Class average   : {analyzer.class_average():.2f}")

    scholar = next(s for s in students if isinstance(s, ScholarshipStudent))
    print(f"\nInheritance chain: {' -> '.join(cls.__name__ for cls in type(scholar).__mro__[:-1])}")
    print(f"Inherited from Student (no new code): grade {scholar.get_grade()}, average {scholar.calculate_average():.2f}")
    print(f"Added in ScholarshipStudent        : amount KES {scholar.scholarship_amount:,.0f}, eligible = {scholar.is_eligible()}")
    print(f"Overridden in ScholarshipStudent   : {scholar.get_status_message()}")


def demo_polymorphism(students):
    """Task 5: same method call, different behaviour per student type."""
    print_heading("TASK 5 - Polymorphism: one method, different behaviour")
    for student in students:  # one list holding different student types
        print(f"{type(student).__name__:<18} {student.full_name:<16} -> {student.get_status_message()}")


def demo_flexible_methods(student):
    """Task 6: *args and default arguments as Python's approach to overloading."""
    print_heading("TASK 6 - Flexible method interface (*args and default arguments)")
    print(f"calculate_average()                  -> {student.calculate_average():.2f}  (own marks)")
    print(f"calculate_average(80, 90, 70)        -> {student.calculate_average(80, 90, 70):.2f}  (three marks)")
    print(f"calculate_average(80, 90, 70, 60, 55)-> {student.calculate_average(80, 90, 70, 60, 55):.2f}  (five marks)")
    print(f"calculate_average(80, 85, 90, decimals=0) -> {student.calculate_average(80, 85, 90, decimals=0):.0f}  (custom rounding)")
    for label, bad_call in (
        ("compute_average()", lambda: Student.compute_average()),
        ("compute_average(80, 120)", lambda: Student.compute_average(80, 120)),
        ("compute_average(80, 'A')", lambda: Student.compute_average(80, "A")),
    ):
        try:
            bad_call()
        except (ValueError, TypeError) as error:
            print(f"Validation {label:<26}: {error}")


def demo_report(analyzer, report_file):
    """Task 7: print and save the full performance report."""
    print_heading("TASK 7 - Full performance report")
    print(analyzer.generate_report())
    analyzer.save_report(report_file)
    print(f"\nReport also saved to: {report_file.name}")
