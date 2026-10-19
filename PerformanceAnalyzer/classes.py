"""
classes.py
All classes for the Student Performance Analysis System.

    Student (abstract)          - encapsulation, abstraction, flexible calculate_average()
      +-- AIUStudent            - regular student, implements the abstract method
            +-- ScholarshipStudent - adds scholarship rules, overrides methods
    PerformanceAnalyzer         - highest, lowest, class average and the full report
"""
from abc import ABC, abstractmethod
from pathlib import Path

# --------------------------------------------------------------------------
# Constants (kept in one place so rules are easy to change)
# --------------------------------------------------------------------------
SUBJECTS = ("Math", "English", "Science")   # subjects stored for every student
MIN_MARK = 0                                # lowest valid mark
MAX_MARK = 100                              # highest valid mark
SCHOLARSHIP_CUTOFF = 85                     # minimum average for scholarship eligibility
REQUIRED_COLUMNS = ("StudentID", "FName", "LName", "Programme") + SUBJECTS


# ==========================================================================
# Student: abstract base class (encapsulation and abstraction)
# ==========================================================================
class Student(ABC):
    """Abstract base class that stores and protects the data of one student."""

    def __init__(self, student_id, first_name, last_name, programme, marks):
        """
        Create a student.

        marks must be a dictionary with one mark for every subject in SUBJECTS,
        for example {"Math": 75, "English": 80, "Science": 70}.
        """
        # Single underscore = protected: meant for this class and its subclasses.
        self._student_id = self._validate_text(student_id, "Student ID")
        self._first_name = self._validate_text(first_name, "First name")
        self._last_name = self._validate_text(last_name, "Last name")
        self._programme = self._validate_text(programme, "Programme")

        # Double underscore = private: name-mangled, only Student's own methods touch it.
        self.__marks = {}
        for subject in SUBJECTS:
            if subject not in marks:
                raise ValueError(f"Missing mark for subject: {subject}")
            self.set_mark(subject, marks[subject])  # reuse the validating setter

    # ---------------- validation helpers (static: need no object data) -------
    @staticmethod
    def _validate_text(value, field_name):
        """Return the stripped text, or raise ValueError if it is empty."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty text value.")
        return value.strip()

    @staticmethod
    def _validate_mark(mark):
        """Return the mark as a float, or raise an error if it is not valid."""
        if isinstance(mark, bool) or not isinstance(mark, (int, float)):
            raise TypeError(f"Marks must be numbers, got {mark!r}.")
        if not MIN_MARK <= mark <= MAX_MARK:
            raise ValueError(f"Marks must be between {MIN_MARK} and {MAX_MARK}, got {mark}.")
        return float(mark)

    # ---------------- encapsulated access: properties ------------------------
    @property
    def student_id(self):
        """Read-only: an ID must never change after the student is created."""
        return self._student_id

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = self._validate_text(value, "First name")

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = self._validate_text(value, "Last name")

    @property
    def programme(self):
        return self._programme

    @programme.setter
    def programme(self, value):
        self._programme = self._validate_text(value, "Programme")

    @property
    def full_name(self):
        """Read-only combination of first and last name."""
        return f"{self._first_name} {self._last_name}"

    # ---------------- marks: controlled access -------------------------------
    def get_marks(self):
        """Return a COPY of the marks so outside code cannot change them directly."""
        return dict(self.__marks)

    def set_mark(self, subject, mark):
        """Update one subject mark after validating the subject and the mark."""
        if subject not in SUBJECTS:
            raise KeyError(f"Unknown subject '{subject}'. Valid subjects: {', '.join(SUBJECTS)}")
        self.__marks[subject] = self._validate_mark(mark)

    # ---------------- calculations -------------------------------------------
    @staticmethod
    def compute_average(*marks, decimals=2):
        """
        Task 6 - flexible interface (Python's equivalent of method overloading).

        Accepts ANY number of marks passed separately (*marks) and an optional
        keyword argument 'decimals' that has a default value of 2.
            compute_average(80, 90, 70)          -> three subjects
            compute_average(80, 90, 70, 60, 55)  -> five subjects
            compute_average(80, 90, decimals=0)  -> custom rounding
        """
        if not marks:
            raise ValueError("At least one mark is required to calculate an average.")
        valid_marks = [Student._validate_mark(mark) for mark in marks]
        return round(sum(valid_marks) / len(valid_marks), decimals)

    @property
    def average_score(self):
        """Full-precision average of the stored marks (used for comparisons)."""
        marks = list(self.__marks.values())
        return sum(marks) / len(marks)

    def calculate_average(self, *marks, decimals=2):
        """
        Calculate an average, using the same flexible interface:
            student.calculate_average()              -> the student's own marks
            student.calculate_average(70, 80, 90)    -> the marks supplied
            student.calculate_average(70, 80, 90, 60)-> any number of marks
        """
        if not marks:
            return round(self.average_score, decimals)
        return self.compute_average(*marks, decimals=decimals)

    @staticmethod
    def grade_for(average):
        """Convert an average into a letter grade."""
        if average >= 80:
            return "A"
        if average >= 70:
            return "B"
        if average >= 60:
            return "C"
        if average >= 50:
            return "D"
        return "F"

    def get_grade(self):
        """Return the student's letter grade based on their average."""
        return self.grade_for(self.average_score)

    # ---------------- abstraction ---------------------------------------------
    @abstractmethod
    def get_status_message(self):
        """
        Abstract method: every concrete student type MUST implement it.
        Student itself cannot be instantiated because this method has no body here.
        """

    # ---------------- reporting (Task 7) ---------------------------------------
    @staticmethod
    def _format_mark(mark):
        """Show 75.0 as 75 and 82.5 as 82.5."""
        return f"{mark:g}"

    def generate_report(self):
        """Return a readable performance report for this student."""
        marks_text = " | ".join(
            f"{subject}: {self._format_mark(mark)}" for subject, mark in self.get_marks().items()
        )
        lines = [
            f"Student ID  : {self.student_id}",
            f"Name        : {self.full_name}",
            f"Programme   : {self.programme}",
            f"Marks       : {marks_text}",
            f"Average     : {self.calculate_average():.2f}",
            f"Grade       : {self.get_grade()}",
            f"Status      : {self.get_status_message()}",
        ]
        return "\n".join(lines)

    def __str__(self):
        return f"{self.student_id} {self.full_name} ({self.programme}) - average {self.calculate_average():.2f}"


# ==========================================================================
# AIUStudent: regular student
# ==========================================================================
class AIUStudent(Student):
    """A regular university student. Implements the abstract method."""

    def get_status_message(self):
        """Implements the abstract method for a regular student."""
        if self.average_score >= 50:
            standing = "Good standing"
        else:
            standing = "Needs academic support"
        return f"Regular student - {standing}, grade {self.get_grade()}."


# ==========================================================================
# ScholarshipStudent: inheritance, super() and method overriding
# ==========================================================================
class ScholarshipStudent(AIUStudent):
    """A student who holds a scholarship; adds eligibility rules to AIUStudent."""

    def __init__(self, student_id, first_name, last_name, programme, marks, scholarship_amount):
        # super() runs AIUStudent/Student's constructor so we do not repeat that code.
        super().__init__(student_id, first_name, last_name, programme, marks)
        self._scholarship_amount = self._validate_amount(scholarship_amount)

    @staticmethod
    def _validate_amount(amount):
        """Scholarship amounts must be non-negative numbers."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError(f"Scholarship amount must be a number, got {amount!r}.")
        if amount < 0:
            raise ValueError("Scholarship amount cannot be negative.")
        return float(amount)

    @property
    def scholarship_amount(self):
        return self._scholarship_amount

    @scholarship_amount.setter
    def scholarship_amount(self, value):
        self._scholarship_amount = self._validate_amount(value)

    def is_eligible(self):
        """True when the average is at least SCHOLARSHIP_CUTOFF (85)."""
        return self.average_score >= SCHOLARSHIP_CUTOFF

    # Overridden method (Task 4 and 5): same name as in AIUStudent, new behaviour.
    def get_status_message(self):
        if self.is_eligible():
            return (f"Scholarship student - eligible, KES {self.scholarship_amount:,.0f} "
                    f"awarded, grade {self.get_grade()}.")
        return (f"Scholarship student - NOT eligible (average below {SCHOLARSHIP_CUTOFF}), "
                f"scholarship of KES {self.scholarship_amount:,.0f} at risk.")

    # Overridden again: reuse the parent report with super() and extend it.
    def generate_report(self):
        base_report = super().generate_report()
        eligibility = "ELIGIBLE" if self.is_eligible() else "NOT ELIGIBLE"
        extra = [
            f"Scholarship : KES {self.scholarship_amount:,.0f}",
            f"Eligibility : {eligibility} (cut-off average {SCHOLARSHIP_CUTOFF})",
        ]
        return base_report + "\n" + "\n".join(extra)


# ==========================================================================
# PerformanceAnalyzer: composition (holds Student objects, never copies them)
# ==========================================================================
class PerformanceAnalyzer:
    """Analyses a collection of Student objects without copying their data."""

    def __init__(self, students):
        students = list(students)  # a list of REFERENCES to the same student objects
        if not students:
            raise ValueError("PerformanceAnalyzer needs at least one student.")
        for student in students:
            if not isinstance(student, Student):
                raise TypeError(f"Expected Student objects, got {type(student).__name__}.")
        self._students = students

    def highest_average(self):
        """Return the Student object with the highest average."""
        return max(self._students, key=lambda student: student.average_score)

    def lowest_average(self):
        """Return the Student object with the lowest average."""
        return min(self._students, key=lambda student: student.average_score)

    def class_average(self):
        """Return the average of all student averages, rounded to 2 decimals."""
        total = sum(student.average_score for student in self._students)
        return round(total / len(self._students), 2)

    def grade_distribution(self):
        """Return how many students got each letter grade."""
        distribution = {grade: 0 for grade in ("A", "B", "C", "D", "F")}
        for student in self._students:
            distribution[student.get_grade()] += 1
        return distribution

    def generate_report(self):
        """Return the full report: every student followed by the class summary."""
        divider = "=" * 64
        thin = "-" * 64
        sections = [divider, "STUDENT PERFORMANCE REPORT".center(64), divider]

        for number, student in enumerate(self._students, start=1):
            sections.append(f"Student {number} of {len(self._students)}")
            sections.append(student.generate_report())  # polymorphism: each type reports itself
            sections.append(thin)

        highest = self.highest_average()
        lowest = self.lowest_average()
        scholars = [s for s in self._students if isinstance(s, ScholarshipStudent)]
        eligible = [s for s in scholars if s.is_eligible()]
        distribution = ", ".join(f"{g}: {n}" for g, n in self.grade_distribution().items())

        sections += [
            "CLASS PERFORMANCE SUMMARY".center(64),
            thin,
            f"Number of students    : {len(self._students)}",
            f"Highest average       : {highest.calculate_average():.2f} - {highest.full_name} ({highest.student_id})",
            f"Lowest average        : {lowest.calculate_average():.2f} - {lowest.full_name} ({lowest.student_id})",
            f"Overall class average : {self.class_average():.2f}",
            f"Grade distribution    : {distribution}",
            f"Scholarship holders   : {len(scholars)} (eligible: {len(eligible)}, not eligible: {len(scholars) - len(eligible)})",
            divider,
        ]
        return "\n".join(sections)

    def save_report(self, file_path):
        """Write the report to a text file."""
        Path(file_path).write_text(self.generate_report(), encoding="utf-8")
