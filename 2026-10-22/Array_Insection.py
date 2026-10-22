
# Array Insertion Program

numbers = []

n = int(input("Enter number of elements: "))

for i in range(n):
    value = int(input("Enter element: "))
    numbers.append(value)

print("Original List:", numbers)

while True:
    print("\n----- INSERTION MENU -----")
    print("1. Append")
    print("2. Insert")
    print("3. Extend")
    print("4. Exit")

    choice = int(input("Enter your choice: "))

    if choice == 1:
        value = int(input("Enter value to append: "))
        numbers.append(value)
        print("After Append:", numbers)

    elif choice == 2:
        index = int(input("Enter index: "))
        value = int(input("Enter value: "))

        if 0 <= index <= len(numbers):
            numbers.insert(index, value)
            print("After Insert:", numbers)
        else:
            print("Invalid index!")

    elif choice == 3:
        count = int(input("How many values? "))
        new_values = []

        for i in range(count):
            value = int(input("Enter value: "))
            new_values.append(value)

        numbers.extend(new_values)
        print("After Extend:", numbers)

    elif choice == 4:
        print("Final List:", numbers)
        print("Program Ended")
        break

    else:
        print("Invalid Choice!")

