import csv

from classes import AIUStudent, ScholarshipStudent, Student


# Task 1: Read the CSV and create student objects

def load_students_from_csv(file_name):
    students = []

    with open(file_name, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            marks = {
                "Math": float(row["Math"]),
                "English": float(row["English"]),
                "Science": float(row["Science"]),
            }

            scholarship_amount = row["ScholarshipAmount"].strip()
            if scholarship_amount == "":
                student = AIUStudent(
                    row["StudentID"], row["FName"], row["LName"],
                    row["Programme"], marks
                )
            else:
                student = ScholarshipStudent(
                    row["StudentID"], row["FName"], row["LName"],
                    row["Programme"], marks, float(scholarship_amount)
                )

            students.append(student)

    return students


# Task 2: Show abstraction and encapsulation

def show_abstraction_and_encapsulation():
    print("TASK 2: ABSTRACTION AND ENCAPSULATION")

    try:
        Student("00/000", "Test", "Student", "MDS", {
            "Math": 50, "English": 50, "Science": 50
        })
    except TypeError:
        print("Student is abstract and cannot be created directly.")

    print("Marks are private and are changed with set_mark().")
    print()


# Task 3: Show the class averages

def show_analyzer(analyzer):
    print("TASK 3: PERFORMANCE ANALYZER")

    highest = analyzer.highest_average()
    lowest = analyzer.lowest_average()

    print("Highest average:", highest.get_full_name(), highest.calculate_average())
    print("Lowest average:", lowest.get_full_name(), lowest.calculate_average())
    print("Class average:", analyzer.class_average())
    print()


# Task 4: Show scholarship inheritance and overriding

def show_inheritance(students):
    print("TASK 4: INHERITANCE AND METHOD OVERRIDING")

    for student in students:
        if isinstance(student, ScholarshipStudent):
            print("Scholarship student:", student.get_full_name())
            print("Scholarship amount: KES", student.scholarship_amount)
            print("Eligible:", student.is_eligible())
            print("Special status:", student.get_status_message())
            print()
            return

    print("No scholarship student was found.")
    print()


# Task 5: Call the same method for different student types

def show_polymorphism(students):
    print("TASK 5: POLYMORPHISM")

    for student in students:
        print(student.get_full_name(), "-", student.get_status_message())
    print()


# Task 6: Use different numbers of marks in one method

def show_flexible_method(student):
    print("TASK 6: FLEXIBLE METHOD")
    print("Average of stored marks:", student.calculate_average())
    print("Average of three marks:", student.calculate_average(80, 90, 70))
    print("Average of five marks:", student.calculate_average(80, 90, 70, 60, 50))
    print("Average rounded to a whole number:",
          student.calculate_average(80, 90, decimals=0))
    print()


# Task 7: Save the report in a text file

def save_report(analyzer, file_name):
    report = analyzer.generate_report()

    with open(file_name, "w", encoding="utf-8") as report_file:
        report_file.write(report)

    print("Report saved to", file_name)
