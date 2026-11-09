# Student Performance Analysis System

**Student:** Leon Gikonyo Muchunga
**Student number:** 251191BSIT

A simple Python program that reads student marks from a CSV file, calculates averages and grades, checks scholarship eligibility, and creates a class report.

## Files

- `main.py` starts the program and runs the examples.
- `classes.py` contains the `Student`, `AIUStudent`, `ScholarshipStudent`, and `PerformanceAnalyzer` classes.
- `methods.py` loads the CSV file and contains small demonstration functions.
- `students.csv` contains the student records. It includes the four sample students and three extra records.
- `performance_report.txt` is created when the program runs.

## Run the program

Open a terminal in this folder and run:

```text
python main.py
```

The program uses only Python's standard library. Keep the CSV file in the same folder as `main.py`.

## How the program meets the assignment

1. **CSV dataset:** `students.csv` has seven student records, including the four records supplied in the assignment. The `ScholarshipAmount` column identifies scholarship students; a blank value means the student is a regular `AIUStudent`.
2. **Encapsulation and abstraction:** `Student` stores its marks in a private `__marks` dictionary. Marks are read with `get_marks()` and changed with `set_mark()`. `Student` is an abstract class because it requires child classes to provide `get_status_message()`.
3. **Analyzer and composition:** `PerformanceAnalyzer` stores a list of student objects and provides `highest_average()`, `lowest_average()`, and `class_average()`.
4. **Inheritance and overriding:** `AIUStudent` inherits from `Student`. `ScholarshipStudent` inherits from `AIUStudent`, uses `super()` to set up common information, and adds `scholarship_amount` and `is_eligible()`. Its `get_status_message()` and `generate_report()` methods override parent methods.
5. **Polymorphism:** the program puts both types in the same student list and calls `get_status_message()` for each object. Python uses the version that belongs to that object's class.
6. **Flexible method:** `calculate_average(*marks, decimals=2)` can calculate the student's stored marks or marks provided in the call. For example, it accepts three marks, five marks, or a different number of decimal places. Python does not use traditional method overloading; `*marks` and a default argument provide flexibility instead.
7. **Report:** running the program prints and saves a report with student IDs, names, programmes, marks, averages, grades, scholarship information where applicable, and the highest, lowest, and class averages.

The grading scale is A (80 and above), B (70–79), C (60–69), D (50–59), and F (below 50). A scholarship student is eligible when their average is at least 85.

## Brief reflection

One challenge was connecting the CSV rows to different student types. I used the `ScholarshipAmount` column to decide whether to create an `AIUStudent` or a `ScholarshipStudent`. Another challenge was showing flexible average calculations, because Python does not support traditional method overloading. The `*marks` argument lets one method accept different numbers of marks.

## AI use declaration

AI assistance was used to simplify and review the program structure and to help check the implementation against the assignment requirements. The submitted student should review the final code, run it, and make sure they understand and can explain each part. This declaration should be adjusted if the course requires a different format or further detail about AI use.
