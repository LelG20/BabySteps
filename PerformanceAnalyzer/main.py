"""
Student Performance Analysis System - main program
Author : Leon Gikonyo Muchunga (251191BSIT)

Run with:  python main.py

Classes live in classes.py and functions in methods.py; this file only
imports them and runs the demonstration for each task.
"""
from pathlib import Path

from classes import PerformanceAnalyzer
from methods import (
    demo_abstraction_and_encapsulation,
    demo_analyzer_and_inheritance,
    demo_flexible_methods,
    demo_loading,
    demo_polymorphism,
    demo_report,
    load_students_from_csv,
)

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "students.csv"
REPORT_FILE = BASE_DIR / "performance_report.txt"


def main():
    students = load_students_from_csv(CSV_FILE)
    analyzer = PerformanceAnalyzer(students)

    demo_loading(students)                              # Task 1
    demo_abstraction_and_encapsulation()                # Task 2
    demo_analyzer_and_inheritance(students, analyzer)   # Tasks 3 and 4
    demo_polymorphism(students)                         # Task 5
    demo_flexible_methods(students[0])                  # Task 6
    demo_report(analyzer, REPORT_FILE)                  # Task 7


if __name__ == "__main__":
    main()
