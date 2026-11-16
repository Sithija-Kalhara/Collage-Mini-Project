from array import array

a = array('i', [10, 15, 20, 25, 30])
even = 0
odd = 0
for i in a:
    if i % 2 == 0:
        even += 1
    else:
        odd += 1
print("Even numbers:", even)
print("Odd numbers:", odd)