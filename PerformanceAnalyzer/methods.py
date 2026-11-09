import csv

from classes import AIUStudent, ScholarshipStudent, Student


def load_students_from_csv(file_name):
    """Read the CSV file and make a list of student objects."""
    students = []

    with open(file_name, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            marks = {
                "Math": float(row["Math"]),
                "English": float(row["English"]),
                "Science": float(row["Science"]),
            }

            scholarship_amount = row.get("ScholarshipAmount", "").strip()

            if scholarship_amount != "":
                student = ScholarshipStudent(
                    row["StudentID"],
                    row["FName"],
                    row["LName"],
                    row["Programme"],
                    marks,
                    float(scholarship_amount),
                )
            else:
                student = AIUStudent(
                    row["StudentID"],
                    row["FName"],
                    row["LName"],
                    row["Programme"],
                    marks,
                )

            students.append(student)

    return students


def show_abstraction_and_encapsulation():
    print("TASK 2: ABSTRACTION AND ENCAPSULATION")

    try:
        Student("00/000", "Test", "Student", "MDS", {
            "Math": 50,
            "English": 50,
            "Science": 50,
        })
    except TypeError:
        print("Student is an abstract class and cannot be created directly.")

    print("Student marks are kept private and changed with set_mark().")
    print()


def show_analyzer(analyzer):
    print("TASK 3: PERFORMANCE ANALYZER")
    print("Highest average:", analyzer.highest_average())
    print("Lowest average:", analyzer.lowest_average())
    print("Class average:", analyzer.class_average())
    print()


def show_inheritance(students):
    print("TASK 4: INHERITANCE AND METHOD OVERRIDING")

    for student in students:
        if isinstance(student, ScholarshipStudent):
            print("Scholarship student:", student.get_full_name())
            print("Scholarship amount: KES", student.scholarship_amount)
            print("Eligible:", student.is_eligible())
            print("Special status:", student.get_status_message())
            break
    print()


def show_polymorphism(students):
    print("TASK 5: POLYMORPHISM")
    print("Each object gives its own status message:")

    for student in students:
        print(student.get_full_name(), "-", student.get_status_message())
    print()


def show_flexible_method(student):
    print("TASK 6: FLEXIBLE METHOD")
    print("Average of this student's subjects:", student.calculate_average())
    print("Average of three marks:", student.calculate_average(80, 90, 70))
    print("Average of five marks:", student.calculate_average(80, 90, 70, 60, 50))
    print("Average rounded to a whole number:", student.calculate_average(80, 90, decimals=0))
    print()


def save_report(analyzer, file_name):
    report = analyzer.generate_report()

    with open(file_name, "w", encoding="utf-8") as report_file:
        report_file.write(report)

    print("Report saved to", file_name)
