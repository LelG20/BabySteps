from classes import PerformanceAnalyzer
from methods import (
    load_students_from_csv,
    save_report,
    show_abstraction_and_encapsulation,
    show_analyzer,
    show_flexible_method,
    show_inheritance,
    show_polymorphism,
)


# Task 1: Load the student records and create the analyzer
students = load_students_from_csv("students.csv")
analyzer = PerformanceAnalyzer(students)

print("STUDENT PERFORMANCE ANALYSIS SYSTEM")
print("Students loaded:", len(students))
print()

# Tasks 2 to 6: Demonstrate the OOP requirements
show_abstraction_and_encapsulation()
show_analyzer(analyzer)
show_inheritance(students)
show_polymorphism(students)
show_flexible_method(students[0])

# Task 7: Print and save the performance report
print("TASK 7: PERFORMANCE REPORT")
print(analyzer.generate_report())
save_report(analyzer, "performance_report.txt")
