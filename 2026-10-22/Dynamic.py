marks = []

n = int(input("Enter the number of students: "))

for i in range(n):
    mark = int(input(f"Enter marks for student {i + 1}: "))
    marks.append(mark)

print("Marks of students:", marks)