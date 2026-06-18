library = { 
    101: "PYthon Basics",
    102: "Data Science",
    103: "Machine Learning"
    }
    
while True:
    print("\n1. View Books")
    print("2. Add Book")
    print("3. Search Book")
    print("4. Exit")
    
    choice = int(input("Enter choice: "))
    
    if choice == 1:
        print(library)
    elif choice == 2:
        book_id = int(input("Enter Book ID: "))
        book_name = input("Enter Book Name: ")
        library[book_id] = book_name
        print("Book Added")
        
    elif choice == 3:
        book_id = int(input("Enter Book ID: "))
        if book_id in library:
            print("Book Name:", library[book_id])
        else:
            print("Book Not Found")
    elif choice == 4:
        break