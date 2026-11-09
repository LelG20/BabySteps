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


# Keep these files in the same folder as main.py.
students = load_students_from_csv("students.csv")
analyzer = PerformanceAnalyzer(students)

print("STUDENT PERFORMANCE ANALYSIS SYSTEM")
print("Students loaded:", len(students))
print()

show_abstraction_and_encapsulation()
show_analyzer(analyzer)
show_inheritance(students)
show_polymorphism(students)
show_flexible_method(students[0])

print("TASK 7: PERFORMANCE REPORT")
print(analyzer.generate_report())
save_report(analyzer, "performance_report.txt")
