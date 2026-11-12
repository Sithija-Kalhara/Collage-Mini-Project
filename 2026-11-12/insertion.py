arr = []

n = int(input("Enter number of elements: "))

for i in range(n):
    num = int(input("Enter element: "))
    arr.append(num)

print("Before sorting:", arr)

# Insertion Sort
for i in range(1, len(arr)):
    key = arr[i]
    j = i - 1

    while j >= 0 and arr[j] > key:
        arr[j + 1] = arr[j]
        j -= 1

    arr[j + 1] = key

print("After sorting:", arr)