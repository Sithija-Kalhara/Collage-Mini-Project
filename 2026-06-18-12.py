cart = []
while True:
    print("\n1. Add Item")
    print("2. View Cart")
    print("3. Remove Item")
    print("4. Exit")
    choice = int(input("Enter choice: "))
    if choice == 1:
        item = input("Enter Item Name: ")
        cart.append(item)
        print(item,"added to cart")
    elif choice == 2:
        print("Shopping Cart: ", cart)
    elif choice == 3:
        item = input("Enteritem to remove: ")
        if item in cart:
            cart.remove(item)
            print(item, "removed")
        else:
            print("Item not found")
    elif choice == 4:
        break