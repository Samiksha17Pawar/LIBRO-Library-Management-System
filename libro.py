import csv
import os
from datetime import date

BOOKS = "books.csv"
TRANS = "transactions.csv"
BOOK_HEAD = ["Book ID", "Book Name", "Author", "Genre", "Category", "Quantity"]
TRANS_HEAD = ["Student ID", "Student Name", "Book ID", "Book Name", "Date", "Status"]
USER, PASS = "admin", "admin123"

def setup():
    if not os.path.exists(BOOKS):
        data = [
            ["B001","The Alchemist","Paulo Coelho","Fiction","Novel",4],
            ["B002","A Brief History of Time","Stephen Hawking","Science","Non-Fiction",3],
            ["B003","Introduction to Algorithms","Thomas Cormen","Computer Science","Textbook",2],
            ["B004","Wings of Fire","A.P.J. Abdul Kalam","Biography","Non-Fiction",5],
            ["B005","Harry Potter","J.K. Rowling","Fantasy","Novel",0],
            ["B006","Clean Code","Robert C. Martin","Computer Science","Textbook",3]
        ]
        write(BOOKS, BOOK_HEAD, [dict(zip(BOOK_HEAD, x)) for x in data])
    if not os.path.exists(TRANS):
        data = [
            ["S001","Rahul Sharma","B005","Harry Potter","2026-09-01","Issued"],
            ["S002","Priya Singh","B003","Introduction to Algorithms","2026-09-05","Issued"]
        ]
        write(TRANS, TRANS_HEAD, [dict(zip(TRANS_HEAD, x)) for x in data])

def read(file):
    try:
        with open(file, newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []
    except Exception as e:
        print("File error:", e)
        return []

def write(file, headers, rows):
    try:
        with open(file, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerows(rows)
    except Exception as e:
        print("File error:", e)

def books():
    data = read(BOOKS)
    for b in data:
        try: b["Quantity"] = int(b["Quantity"])
        except (ValueError, TypeError): b["Quantity"] = 0
    return data

def header(title):
    print("\n" + "=" * 62)
    print(title.center(62))
    print("=" * 62)

def table(headers, rows):
    if not rows:
        print("No records found.")
        return
    widths = [len(str(x)) for x in headers]
    for row in rows:
        for i, x in enumerate(row):
            widths[i] = max(widths[i], len(str(x)))
    line = " | ".join(str(x).ljust(widths[i]) for i, x in enumerate(headers))
    print(line)
    print("-" * len(line))
    for row in rows:
        print(" | ".join(str(x).ljust(widths[i]) for i, x in enumerate(row)))

def text(prompt):
    while True:
        value = input(prompt).strip()
        if value: return value
        print("This field cannot be empty.")

def number(prompt):
    while True:
        try:
            n = int(input(prompt).strip())
            if n >= 0: return n
            print("Value cannot be negative.")
        except ValueError:
            print("Enter a valid whole number.")

def find(data, book_id):
    return next((b for b in data if b["Book ID"].lower() == book_id.lower()), None)

def book_rows(data):
    return [[b["Book ID"], b["Book Name"], b["Author"], b["Genre"],
             b["Category"], b["Quantity"],
             "Available" if b["Quantity"] > 0 else "Out of Stock"] for b in data]

def login():
    header("LIBRO - LIBRARY MANAGEMENT SYSTEM")
    print("Please login to continue.\n")
    for attempt in range(3):
        entered_user = input("Username: ").strip()
        entered_pass = input("Password: ").strip()
        if entered_user == USER and entered_pass == PASS:
            print("\nLogin successful!")
            return True
        print("Invalid login. Attempts left:", 2 - attempt)
    print("Too many failed attempts.")
    return False

def dashboard():
    b, t = books(), read(TRANS)
    available = sum(x["Quantity"] for x in b)
    issued = sum(x["Status"] == "Issued" for x in t)
    borrowers = {x["Student ID"].lower() for x in t if x["Status"] == "Issued"}
    header("DASHBOARD")
    print("Total Books      :", available + issued)
    print("Available Copies :", available)
    print("Currently Issued :", issued)
    print("Active Borrowers :", len(borrowers))

def add_book():
    header("ADD BOOK")
    b = books()
    bid = text("Book ID: ")
    if find(b, bid):
        print("Book ID already exists.")
        return
    row = {
        "Book ID": bid, "Book Name": text("Book Name: "),
        "Author": text("Author: "), "Genre": text("Genre: "),
        "Category": text("Category: "), "Quantity": number("Quantity: ")
    }
    b.append(row)
    write(BOOKS, BOOK_HEAD, b)
    print("Book added successfully.")

def view_books():
    header("ALL BOOKS")
    table(BOOK_HEAD + ["Status"], book_rows(books()))

def search_book():
    header("SEARCH BOOK")
    fields = {"1":"Book ID","2":"Book Name","3":"Author","4":"Genre","5":"Category"}
    print("1. Book ID  2. Book Name  3. Author  4. Genre  5. Category")
    field = fields.get(input("Choose field (1-5): ").strip())
    if not field:
        print("Invalid choice.")
        return
    key = text("Search: ").lower()
    matches = [b for b in books() if key in b[field].lower()]
    table(BOOK_HEAD + ["Status"], book_rows(matches))

def update_book():
    header("UPDATE BOOK")
    b = books()
    book = find(b, text("Book ID: "))
    if not book:
        print("Book ID not found.")
        return
    for field in ["Book Name","Author","Genre","Category"]:
        value = input(f"{field} [{book[field]}]: ").strip()
        if value: book[field] = value
    value = input(f"Quantity [{book['Quantity']}]: ").strip()
    if value:
        try:
            if int(value) >= 0: book["Quantity"] = int(value)
            else: print("Quantity cannot be negative; old value kept.")
        except ValueError:
            print("Invalid quantity; old value kept.")
    write(BOOKS, BOOK_HEAD, b)
    print("Book updated successfully.")

def delete_book():
    header("DELETE BOOK")
    b = books()
    book = find(b, text("Book ID: "))
    if not book:
        print("Book ID not found.")
        return
    if any(t["Book ID"].lower() == book["Book ID"].lower() and t["Status"] == "Issued"
           for t in read(TRANS)):
        print("Cannot delete: book is currently issued.")
        return
    if input(f"Delete '{book['Book Name']}'? (y/n): ").lower() == "y":
        b.remove(book)
        write(BOOKS, BOOK_HEAD, b)
        print("Book deleted successfully.")
    else:
        print("Deletion cancelled.")

def issue_book():
    header("ISSUE BOOK")
    b = books()
    book = find(b, text("Book ID: "))
    if not book:
        print("Book ID not found.")
        return
    if book["Quantity"] <= 0:
        print("Book is out of stock.")
        return
    sid, name = text("Student ID: "), text("Student Name: ")
    t = read(TRANS)
    if any(x["Student ID"].lower() == sid.lower() and
           x["Book ID"].lower() == book["Book ID"].lower() and x["Status"] == "Issued" for x in t):
        print("This student already has this book.")
        return
    book["Quantity"] -= 1
    write(BOOKS, BOOK_HEAD, b)
    t.append(dict(zip(TRANS_HEAD, [sid, name, book["Book ID"], book["Book Name"],
                                   str(date.today()), "Issued"])))
    write(TRANS, TRANS_HEAD, t)
    print("Book issued successfully.")

def return_book():
    header("RETURN BOOK")
    sid = text("Student ID: ")
    t = read(TRANS)
    issued = [x for x in t if x["Student ID"].lower() == sid.lower() and x["Status"] == "Issued"]
    if not issued:
        print("No active issued books found.")
        return
    table(["Book ID","Book Name","Date"], [[x["Book ID"],x["Book Name"],x["Date"]] for x in issued])
    bid = text("Book ID to return: ")
    match = next((x for x in issued if x["Book ID"].lower() == bid.lower()), None)
    if not match:
        print("That book is not issued to this student.")
        return
    match["Status"] = "Returned"
    write(TRANS, TRANS_HEAD, t)
    b = books()
    book = find(b, bid)
    if book:
        book["Quantity"] += 1
        write(BOOKS, BOOK_HEAD, b)
    print("Book returned successfully.")

def history():
    header("ISSUE HISTORY")
    t = read(TRANS)
    table(TRANS_HEAD, [[x[h] for h in TRANS_HEAD] for x in t])

def menu():
    actions = {"1":dashboard,"2":add_book,"3":view_books,"4":search_book,
               "5":update_book,"6":delete_book,"7":issue_book,
               "8":return_book,"9":history}
    while True:
        header("LIBRO - MAIN MENU")
        print("1. Dashboard\n2. Add Book\n3. View All Books\n4. Search Book")
        print("5. Update Book\n6. Delete Book\n7. Issue Book\n8. Return Book")
        print("9. Issue History\n10. Logout\n11. Exit")
        choice = input("\nEnter choice (1-11): ").strip()
        if choice in actions:
            actions[choice]()
            input("\nPress Enter to continue...")
        elif choice == "10":
            return "logout"
        elif choice == "11":
            print("Thank you for using LIBRO!")
            return "exit"
        else:
            print("Invalid choice.")

def main():
    setup()
    while login():
        if menu() == "exit":
            break

if __name__ == "__main__":
    main()