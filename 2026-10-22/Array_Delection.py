
# Array Deletion Program

numbers = []

n = int(input("Enter number of elements: "))

for i in range(n):
    value = int(input("Enter element: "))
    numbers.append(value)

print("Original List:", numbers)

while True:
    print("\n----- DELETION MENU -----")
    print("1. Remove")
    print("2. Pop")
    print("3. Del")
    print("4. Clear")
    print("5. Exit")

    choice = int(input("Enter your choice: "))

    if choice == 1:
        value = int(input("Enter value to remove: "))

        if value in numbers:
            numbers.remove(value)
            print("After Remove:", numbers)
        else:
            print("Value not found!")

    elif choice == 2:
        index = int(input("Enter index to pop: "))

        if 0 <= index < len(numbers):
            removed = numbers.pop(index)
            print("Removed element:", removed)
            print("After Pop:", numbers)
        else:
            print("Invalid index!")

    elif choice == 3:
        index = int(input("Enter index to delete: "))

        if 0 <= index < len(numbers):
            del numbers[index]
            print("After Del:", numbers)
        else:
            print("Invalid index!")

    elif choice == 4:
        numbers.clear()
        print("After Clear:", numbers)

    elif choice == 5:
        print("Final List:", numbers)
        print("Program Ended")
        break

    else:
        print("Invalid Choice!")

