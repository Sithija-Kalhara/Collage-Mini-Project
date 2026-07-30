def even_series(limit):
    print("\nEven Series:")
    for i in range(2, limit + 1, 2):
        if i % 2 == 0:
            print(i)

def odd_series(limit):
    print("\nOdd Series:")
    for i in range(1, limit + 1, 2):
        if i % 2 != 0:
            print(i)

number = int(input("Enter the limit: "))

even_series(number)
odd_series(number)