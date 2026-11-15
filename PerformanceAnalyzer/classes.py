from abc import ABC, abstractmethod

SUBJECTS = ["Math", "English", "Science"]


# Task 2: Student class, encapsulation and abstraction
class Student(ABC):
    def __init__(self, student_id, first_name, last_name, programme, marks):
        self._student_id = student_id
        self._first_name = first_name
        self._last_name = last_name
        self._programme = programme

        # Keep the marks private and validate each one.
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
        # Return a copy so marks are changed through set_mark().
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
        # Use stored marks unless other marks are supplied.
        if len(marks) == 0:
            marks = list(self.__marks.values())
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
        # Keep the exact average for grade and scholarship decisions.
        total = 0
        for mark in self.__marks.values():
            total = total + mark
        return total / len(self.__marks)

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
        pass

    def generate_report(self):
        marks = self.get_marks()
        report = "Student ID  : " + self.get_student_id() + "\n"
        report += "Name        : " + self.get_full_name() + "\n"
        report += "Programme   : " + self.get_programme() + "\n"
        report += "Marks       : Math: " + str(marks["Math"])
        report += ", English: " + str(marks["English"])
        report += ", Science: " + str(marks["Science"]) + "\n"
        report += "Average     : " + str(self.calculate_average()) + "\n"
        report += "Grade       : " + self.get_grade() + "\n"
        report += "Status      : " + self.get_status_message()
        return report


# Task 2: AIUStudent inherits from Student
class AIUStudent(Student):
    def get_status_message(self):
        if self.get_average_score() >= 50:
            return "Regular student in good standing"
        else:
            return "Regular student needs academic support"


# Task 4: ScholarshipStudent inherits and overrides methods
class ScholarshipStudent(AIUStudent):
    def __init__(self, student_id, first_name, last_name, programme, marks,
                 scholarship_amount):
        # Reuse the Student constructor through the parent class.
        super().__init__(student_id, first_name, last_name, programme, marks)
        self.scholarship_amount = scholarship_amount

    def is_eligible(self):
        return self.get_average_score() >= 85

    def get_status_message(self):
        if self.is_eligible():
            return "Scholarship student - eligible"
        else:
            return "Scholarship student - not eligible"

    def generate_report(self):
        report = super().generate_report()
        report += "\nScholarship : KES " + str(self.scholarship_amount)
        if self.is_eligible():
            report += "\nEligible    : Yes"
        else:
            report += "\nEligible    : No"
        return report


# Task 3: Analyzer stores and compares Student objects
class PerformanceAnalyzer:
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
        report = "STUDENT PERFORMANCE REPORT\n"
        report += "=" * 40 + "\n"

        for student in self.students:
            # The student's own class creates its report section.
            report += student.generate_report() + "\n"
            report += "-" * 40 + "\n"

        highest = self.highest_average()
        lowest = self.lowest_average()
        report += "CLASS SUMMARY\n"
        report += "Number of students: " + str(len(self.students)) + "\n"
        report += "Highest average: " + highest.get_full_name()
        report += " (" + str(highest.calculate_average()) + ")\n"
        report += "Lowest average: " + lowest.get_full_name()
        report += " (" + str(lowest.calculate_average()) + ")\n"
        report += "Class average: " + str(self.class_average())
        return report
