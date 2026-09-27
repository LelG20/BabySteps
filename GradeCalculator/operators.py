#Calculate total and average marks for three units
unit1 = 65
unit2 = 79
unit3 = 90

total = unit1 + unit2 + unit3
print("Total marks:", total)
average = total / 3
print("Average marks:", average)


# Use comparison and logical operators to determine whether the student meets a pass condition

if average >= 40:
    print("Congrats! You Passed!")
else:
    print("Womp Womp! You Failed.")