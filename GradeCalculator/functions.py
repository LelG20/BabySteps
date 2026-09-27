#Create calculate_average(marks) and classify_result(average)
def calculate_average(grades):
    total = sum(grades)
    average = total / len(grades)
    return total, average

def classify_result(average):
    if average >= 80:
        return "Distinction Achieved! Well Done Champ!"
    elif average >= 50:
        return "You Passed! Keep Aiming Higher!"
    else:
        return "You Had One Job Man! Failure!"

#Call both from a main section of the program.    
math = 30
english = 60
science = 40

grades = [math, english, science]
total, average = calculate_average(grades)
result = classify_result(average)

print(f"Total: {total:.2f}, Average: {average:.2f}")
print(result)