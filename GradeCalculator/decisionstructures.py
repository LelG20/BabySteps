#Calculate total and average marks for three units
math = 30
english = 60
science = 40

total = math + english + science
print("Total marks:", total)
average = total / 3
print("Average marks:", average)

#Write a grading program using if/elif/else. Extend it to classify results as Distinction, Pass, or Fail.​

if average >= 80:
    print("Distinction Achieved! Well Done Champ!")
elif average >= 50:
    print("You Passed! Keep Aiming Higher!")
else:
    print("You Had One Job Man! Failure!")