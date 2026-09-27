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