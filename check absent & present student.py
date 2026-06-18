all_students = {101, 102, 103, 104, 105}
present_students = set()

n = int(input("How many students are present? "))

for i in range(n):
    roll = int(input("Enter Roll Number: "))
    present_students.add(roll)
    
absent_students = all_students - present_students

print("Present Students: ", present_students)
print("Absent Students: ", absent_students)