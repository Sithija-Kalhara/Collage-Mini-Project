def factorial(num):
    fact = 1
    for i in range(1, num + 1):
        fact = fact * i
    print("Factorial = ", fact)

num = int(input("Enter a number: "))
factorial(num)