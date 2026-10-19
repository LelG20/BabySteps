# Student Performance Analysis System

**Name:** Leon Gikonyo Muchunga  
**Student number:** 251191BSIT

A Python OOP program that loads student records from a CSV file, calculates performance metrics, identifies scholarship-eligible students and generates a performance report.

## Files
| File | Purpose |
|---|---|
| `main.py` | Short main program: imports what it needs and runs each task |
| `classes.py` | All classes: `Student`, `AIUStudent`, `ScholarshipStudent`, `PerformanceAnalyzer`, plus the constants |
| `methods.py` | Stand-alone functions: `load_students_from_csv()` and one demonstration function per task |
| `students.csv` | Dataset: the 4 sample records plus 3 additional records |
| `performance_report.txt` | Report produced by the last run |

## How to run
```
python main.py
```
Requires Python 3.8 or later and only the standard library. Keep `main.py`, `classes.py`, `methods.py` and `students.csv` in the same folder.

## Class design
```
Student (abstract)
   └── AIUStudent                (implements get_status_message)
          └── ScholarshipStudent (adds scholarship_amount, is_eligible; overrides get_status_message and generate_report)

PerformanceAnalyzer  ──holds──>  Student objects (composition)
```

## How the files import each other
```
classes.py   (imports nothing from this project)
methods.py   <- classes.py
main.py      <- classes.py, methods.py
```
Imports only point one way, so there are no circular imports.

## Where each task is met
| Task | Where in the code |
|---|---|
| 1. Dataset | `students.csv` and `load_students_from_csv()` in `methods.py`. Rows with a `ScholarshipAmount` become `ScholarshipStudent` objects, the rest `AIUStudent` objects |
| 2. Encapsulation and abstraction | `classes.py`: `Student` uses protected attributes (`_first_name`), a private marks dictionary (`__marks`), properties and validating setters. `get_status_message()` is an `@abstractmethod`, so `Student` cannot be instantiated |
| 3. PerformanceAnalyzer | `classes.py`: `PerformanceAnalyzer` has `highest_average()`, `lowest_average()`, `class_average()`. It keeps references to the student objects and never copies their data |
| 4. Inheritance and overriding | `classes.py`: `ScholarshipStudent` calls `super().__init__()`, adds `scholarship_amount` and `is_eligible()` (average at least 85), and overrides `get_status_message()` and `generate_report()` |
| 5. Polymorphism | `demo_polymorphism()` in `methods.py` stores both student types in one list and calls `get_status_message()` in a loop |
| 6. Flexible interface | `classes.py`: `calculate_average(*marks, decimals=2)` and `compute_average()` |
| 7. Report | `generate_report()` in the `Student`, `ScholarshipStudent` and `PerformanceAnalyzer` classes (`classes.py`) |

## Explanation: polymorphism and method overriding (Task 5)
`Student` declares `get_status_message()` as abstract. `AIUStudent` implements it with a regular-student message. `ScholarshipStudent` overrides it with a message about the scholarship amount and eligibility. In the loop `for student in students: student.get_status_message()` the code never checks the type. Python looks at the actual object and runs the matching version, so the same call gives different results. The same happens with `generate_report()`: `ScholarshipStudent` reuses the parent's report through `super()` and adds scholarship lines.

## Explanation: method overloading equivalent (Task 6)
Python keeps only the last method defined with a given name, so true overloading is not possible. `calculate_average(*marks, decimals=2)` gives the same flexibility with one method:
- `calculate_average()` uses the student's own stored marks.
- `calculate_average(80, 90, 70)` averages three marks passed separately.
- `calculate_average(80, 90, 70, 60, 55)` averages any number of marks, because `*marks` collects them into a tuple.
- `decimals` is a default argument, so rounding is optional.

Validation rejects an empty call, non-numeric values, booleans and marks outside 0 to 100.

## Grading and eligibility rules
| Average | Grade |
|---|---|
| 80 and above | A |
| 70 to 79.99 | B |
| 60 to 69.99 | C |
| 50 to 59.99 | D |
| Below 50 | F |

A scholarship student is **eligible** when the average is at least 85. The dataset includes one scholarship holder (Brian Kamau) below the cut-off to show the "not eligible" result.

## Sample output (summary)
```
Highest average       : 92.33 - Ruth Mwimali (25/228)
Lowest average        : 48.33 - Faith Achieng (25/234)
Overall class average : 73.71
Grade distribution    : A: 3, B: 2, C: 1, D: 0, F: 1
Scholarship holders   : 3 (eligible: 2, not eligible: 1)
```
The full report is in `performance_report.txt`.

## Reflection on challenges
- **Keeping data protected but usable.** I had to decide what needs a setter and what must not change. The student ID is read-only, and `get_marks()` returns a copy so outside code cannot edit marks without validation.
- **Choosing how to represent two student types in one CSV.** I added an optional `ScholarshipAmount` column. A blank value gives an `AIUStudent`, and a value gives a `ScholarshipStudent`.
- **Rounding.** Comparing rounded averages could wrongly decide eligibility (for example 84.996 shown as 85.00). I compare with the full-precision `average_score` and round only for display.
- **Method overloading in Python.** I had to learn that overloading does not exist and replace it with `*args` and default arguments.
- **Bad data.** The loader skips invalid CSV rows with a warning instead of crashing.

## AI use declaration
I used an AI assistant (Claude, by Anthropic) while working on this assignment. It generated the first draft of the code structure, the extra dataset records and the explanations in this README. I ran the program, checked the output against the task requirements and the averages by hand, and I can explain every class, method and design decision. Any parts I could not explain, I did not keep.
