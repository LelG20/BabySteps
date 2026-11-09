from abc import ABC, abstractmethod

SUBJECTS = ["Math", "English", "Science"]


class Student(ABC):
    """Base class for a student."""

    def __init__(self, student_id, first_name, last_name, programme, marks):
        # The underscore means these fields are intended for class use.
        self._student_id = student_id
        self._first_name = first_name
        self._last_name = last_name
        self._programme = programme

        # Double underscore makes the marks private to this class.
        self.__marks = {}
        for subject in SUBJECTS:
            if subject not in marks:
                raise ValueError("Missing mark for " + subject)
            self.set_mark(subject, marks[subject])

    def get_student_id(self):
        return self._student_id

    def get_full_name(self):
        return self._first_name + " " + self._last_name

    def get_programme(self):
        return self._programme

    def update_name(self, first_name, last_name):
        self._first_name = first_name
        self._last_name = last_name

    def update_programme(self, programme):
        self._programme = programme

    def get_marks(self):
        # Return a copy so other code cannot change marks without set_mark().
        return self.__marks.copy()

    def set_mark(self, subject, mark):
        if subject not in SUBJECTS:
            raise ValueError("Subject must be Math, English, or Science")
        if not isinstance(mark, (int, float)) or isinstance(mark, bool):
            raise ValueError("A mark must be a number")
        if mark < 0 or mark > 100:
            raise ValueError("A mark must be between 0 and 100")
        self.__marks[subject] = mark

    def calculate_average(self, *marks, decimals=2):
        """Average own marks, or any marks passed to this method."""
        if len(marks) == 0:
            marks = tuple(self.__marks.values())

        if len(marks) == 0:
            raise ValueError("At least one mark is needed")

        total = 0
        for mark in marks:
            if not isinstance(mark, (int, float)) or isinstance(mark, bool):
                raise ValueError("Marks must be numbers")
            if mark < 0 or mark > 100:
                raise ValueError("Marks must be between 0 and 100")
            total = total + mark

        return round(total / len(marks), decimals)

    def get_average_score(self):
        """Return the exact average for comparisons and calculations."""
        return sum(self.__marks.values()) / len(self.__marks)

    def get_grade(self):
        average = self.get_average_score()
        if average >= 80:
            return "A"
        elif average >= 70:
            return "B"
        elif average >= 60:
            return "C"
        elif average >= 50:
            return "D"
        else:
            return "F"

    @abstractmethod
    def get_status_message(self):
        """Each type of student must provide its own status message."""
        pass

    def generate_report(self):
        marks = self.get_marks()
        lines = []
        lines.append("Student ID  : " + self.get_student_id())
        lines.append("Name        : " + self.get_full_name())
        lines.append("Programme   : " + self.get_programme())
        lines.append(
            "Marks       : Math: {0}, English: {1}, Science: {2}".format(
                marks["Math"], marks["English"], marks["Science"]
            )
        )
        lines.append("Average     : " + str(self.calculate_average()))
        lines.append("Grade       : " + self.get_grade())
        lines.append("Status      : " + self.get_status_message())
        return "\n".join(lines)

    def __str__(self):
        return self.get_full_name() + " - average " + str(self.calculate_average())


class AIUStudent(Student):
    """A regular student at the university."""

    def get_status_message(self):
        if self.calculate_average() >= 50:
            return "Regular student in good standing"
        else:
            return "Regular student needs academic support"


class ScholarshipStudent(AIUStudent):
    """A student who has a scholarship amount recorded."""

    def __init__(self, student_id, first_name, last_name, programme, marks, scholarship_amount):
        # Use the parent class constructor for the common student information.
        super().__init__(student_id, first_name, last_name, programme, marks)
        self.scholarship_amount = scholarship_amount

    def is_eligible(self):
        return self.get_average_score() >= 85

    # This method overrides AIUStudent.get_status_message().
    def get_status_message(self):
        if self.is_eligible():
            return "Scholarship student - eligible"
        else:
            return "Scholarship student - not eligible"

    # This report also overrides the report from Student.
    def generate_report(self):
        report = super().generate_report()
        if self.is_eligible():
            eligibility = "Yes"
        else:
            eligibility = "No"
        report = report + "\nScholarship : KES " + str(self.scholarship_amount)
        report = report + "\nEligible    : " + eligibility
        return report


class PerformanceAnalyzer:
    """Calculates summary information for a list of Student objects."""

    def __init__(self, students):
        if len(students) == 0:
            raise ValueError("The student list cannot be empty")
        self.students = students

    def highest_average(self):
        highest = self.students[0]
        for student in self.students:
            if student.get_average_score() > highest.get_average_score():
                highest = student
        return highest

    def lowest_average(self):
        lowest = self.students[0]
        for student in self.students:
            if student.get_average_score() < lowest.get_average_score():
                lowest = student
        return lowest

    def class_average(self):
        total = 0
        for student in self.students:
            total = total + student.get_average_score()
        return round(total / len(self.students), 2)

    def generate_report(self):
        report_lines = []
        report_lines.append("STUDENT PERFORMANCE REPORT")
        report_lines.append("=" * 40)

        for student in self.students:
            # The method used depends on the actual student object.
            report_lines.append(student.generate_report())
            report_lines.append("-" * 40)

        highest = self.highest_average()
        lowest = self.lowest_average()

        report_lines.append("CLASS SUMMARY")
        report_lines.append("Number of students: " + str(len(self.students)))
        report_lines.append(
            "Highest average: {0} ({1})".format(
                highest.get_full_name(), highest.calculate_average()
            )
        )
        report_lines.append(
            "Lowest average: {0} ({1})".format(
                lowest.get_full_name(), lowest.calculate_average()
            )
        )
        report_lines.append("Class average: " + str(self.class_average()))
        return "\n".join(report_lines)
