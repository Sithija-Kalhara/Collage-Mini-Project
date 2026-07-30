def factorial(n):
    if n < 0:
        return "Factorial does not exit"
    elif n == 0:
        return 1
    else:
        fact = 1
        i = 1
        while i <= n:
            fact = fact * i
            i = i + 1
        return fact

num = int(input("Enter a number: "))
result = factorial(num)
print(f"The factorial of ",num, "is",result)