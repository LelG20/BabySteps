import os

student_name = input("Enter the student's name: ")

grade1 = float(input("Enter the grade for unit 1: "))
grade2 = float(input("Enter the grade for unit 2: "))
grade3 = float(input("Enter the grade for unit 3: "))

os.system('clear')

grades = [grade1, grade2, grade3]



import grading_utils


total, average = grading_utils.calculate_average(grades)

result = grading_utils.classify_result(average)

print("=" * 40)
print("           STUDENT REPORT           ")
print("=" * 40)
print(f"Name: {student_name}")
print("Grades entered:")
for mark in grades:
    print(mark)
print(f"Total: {total:.2f}")
print(f"Average Mark: {average:.2f}")  # :.2f rounds to 2 decimal places
print(f"Final Grade: {result}")
print("=" * 40)