import sqlite3
conn = sqlite3.connect("C:\\Users\\Admin\\OneDrive\\Desktop\\CMPT 354\\miniproject\\miniproject\\library.db")
cursor = conn.cursor()
from datetime import date
import re

print("\nSup loser, checking out a library database because you have no friends?")
print("nI figured, anyways have fun ig")

def check_membership():
    print("\n\n---------------------------------------")
    print("\nDo you have an existing membership with us?")
    answer = input("Enter (y) for Yes or (n) for No: ").lower()

    if answer == 'n':
        print("\nReally? Ok time to sign up ig")
        create_membership()
        return True  # After creating a membership, we assume the user is now valid
    elif answer == 'y':
        print("Of course you do hahaha")
        email = input("Please enter your email: ")
        query = "SELECT * FROM Member WHERE email = ?"
        cursor.execute(query, (email,))
        member = cursor.fetchone()

        if member:
            print(f"\nWelcome back, {member[1]}!")
            return True  # Membership is valid, user can proceed
        else:
            print("Invalid input. Please try again.")
            return check_membership()  # Retry in case of invalid input
    else:
        print("Invalid input. Please try again.")
        return check_membership()  # Retry in case of invalid input


def create_membership():
    print("\nTo access the library, you need to create a membership.")

    # No validation for name
    name = input("Enter your full name: ")

    # Validate birthday format (YYYY-MM-DD)
    while True:
        birthday = input("Enter your full birthday in this format (YYYY-MM-DD): ")
        if re.match(r"^\d{4}-\d{2}-\d{2}$", birthday):
            break
        print("\nInvalid date format. Please enter in YYYY-MM-DD format.")

    # Validate email format and check if it already exists in the database
    while True:
        email = input("Enter your email: ")

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            print("\nInvalid email. Please enter a valid email address.")
            continue  # Restart email input

        # Check if email is already in the database
        cursor.execute("SELECT email FROM Member WHERE email = ?", (email,))
        if cursor.fetchone():
            print("\nThis email is already registered. Redirecting to membership check...\n")
            check_membership()
            return  # Exit function to avoid creating a duplicate membership

        break  # If email is valid and does not exist, proceed

    # If all inputs are valid, insert into database
    query = '''INSERT INTO Member (name, birthday, email) 
               VALUES (?, ?, ?)'''
    cursor.execute(query, (name, birthday, email))
    conn.commit()

    print(f"\nMembership created successfully for {name}. Welcome to our library!")




def introPage():
    print("\n\n---------------------------------------")
    print("Please input the number of the option you would like: \n")
    print("(1): Find an item in the library ")
    print("(2): Borrow an item from the library ")
    print("(3): Return a borrowed item ")
    print("(4): Donate an item to the library ")
    print("(5): Find an event in the library ")
    print("(6): Register for an event in the library ")
    print("(7): Volunteer for the library ")
    print("(8): Ask for help from a librarian ")
    print("(9): Exit Program ")
    return input("Enter Number: ")

def find_item():
    print("\nPlease enter either the Name, Author, or Genre of the item you're looking for: ")
    item_type = input("(1) Name, (2) Author, (3) Genre: ")

    if item_type == '1':
        search_value = input('Enter the item name (partial match allowed): ')
        query = 'SELECT itemID FROM Item WHERE name LIKE ?'
    elif item_type == '2':
        search_value = input("Enter the author name (partial match allowed): ")
        query = 'SELECT itemID FROM Item WHERE author LIKE ?'
    elif item_type == '3':
        search_value = input('Enter the genre (partial match allowed): ')
        query = 'SELECT itemID FROM Item WHERE genre LIKE ?'
    else:
        print('Invalid choice')
        return
    
    # Add '%' before and after the search value to allow partial matching
    search_value = '%' + search_value + '%'

    cursor.execute(query, (search_value,))
    itemIDs = cursor.fetchall()

    if itemIDs:
        available_items = []
        unavailable_items = []

        # Step 1: Retrieve and classify items
        for itemID in itemIDs:
            cursor.execute("SELECT * FROM Item WHERE itemID = ?", (itemID[0],))
            item_attributes = cursor.fetchone()

            if item_attributes[5].lower() == 'available':
                available_items.append(item_attributes)
            else:
                unavailable_items.append(item_attributes)

        # Step 2: Print available items
        if available_items:
            print("\nAvailable Items:")
            for item in available_items:
                print(f"ItemID: {item[0]}, Name: {item[1]}, Author: {item[2]}, Category: {item[3]}, Genre: {item[4]}, Status: {item[5]}")
        else:
            print("\nNo available items found.")

        # Step 3: Print unavailable items
        if unavailable_items:
            print("\nUnavailable Items:")
            for item in unavailable_items:
                print(f"ItemID: {item[0]}, Name: {item[1]}, Author: {item[2]}, Category: {item[3]}, Genre: {item[4]}, Status: {item[5]}")
        else:
            print("\nNo unavailable items found.")

    else:
        print("\nNo item found matching your search input :(")




def borrow_item():
    print("\n\n---------------------------------------")
    email = input("\nEnter your email: ")

    # Step 1: Check if the email exists in the Member table
    cursor.execute("SELECT * FROM Member WHERE email = ?", (email,))
    member = cursor.fetchone()
    if not member:
        print("\nNo membership found with this email. Please create a membership first.")
        return

    # Step 2: Ask for the item ID to borrow
    item_id = input("\nEnter the item ID of the item you want to borrow: ")

    # Step 3: Check if the item exists and is available
    cursor.execute("SELECT status FROM Item WHERE itemID = ?", (item_id,))
    item = cursor.fetchone()
    if item is None:
        print("\nItem not found.")
        return
    status = item[0]
    if status == 'Unavailable':
        print("\nThe item is currently Unavailable for borrowing.")
        return

    # Step 4: Insert the borrow record into Borrow table
    cursor.execute("INSERT INTO Borrow (email, itemID) VALUES (?, ?)", (email, item_id))
    conn.commit()

    # Step 5: Insert into BorrowTransactions with NULL borrowID and retrieve borrowID
    borrow_date = date.today().strftime("%Y-%m-%d")  # Get current date
    cursor.execute("INSERT INTO BorrowTransactions (borrowID, borrowDate) VALUES (NULL, ?)", (borrow_date,))
    conn.commit()

    # Step 6: Retrieve the generated borrowID
    borrow_id = cursor.lastrowid

    # Step 7: Update Borrow table with the new borrowID
    cursor.execute("UPDATE Borrow SET borrowID = ? WHERE email = ? AND itemID = ?", (borrow_id, email, item_id))
    conn.commit()

    # Step 8: Retrieve the return date assigned by the trigger
    cursor.execute("SELECT returnDate FROM BorrowTransactions WHERE borrowID = ?", (borrow_id,))
    return_date = cursor.fetchone()[0]

    # Step 9: Mark the item as unavailable
    cursor.execute("UPDATE Item SET status = 'Unavailable' WHERE itemID = ?", (item_id,))
    conn.commit()

    # Step 10: Confirm success to the user
    cursor.execute("SELECT name FROM Item WHERE itemID = ?", (item_id,))
    item_name = cursor.fetchone()[0]

    print(f"\nSuccess! You borrowed '{item_name}'.")
    print(f"Return Date: {return_date}")
        

def return_item():
    print("\n\n---------------------------------------")
    email = input("\nEnter your email: ")

    # Step 1: Check if the email exists in the Member table
    cursor.execute("SELECT * FROM Member WHERE email = ?", (email,))
    member = cursor.fetchone()
    if not member:
        print("\nNo membership found with this email.")
        return

    # Step 2: Ask for the item ID to return
    item_id = input("\nEnter the item ID of the item you want to return: ")

    # Step 3: Check if the item is currently borrowed by the user
    cursor.execute("SELECT borrowID FROM Borrow WHERE email = ? AND itemID = ?", (email, item_id))
    borrow_record = cursor.fetchone()

    if borrow_record is None:
        print("\nYou have not borrowed this item or it does not exist.")
        return

    borrow_id = borrow_record[0]  # Get borrowID from the tuple

    # Step 4: Update the status of the item to "Available"
    cursor.execute("UPDATE Item SET status = 'Available' WHERE itemID = ?", (item_id,))
    conn.commit()

    # Step 5: Update the BorrowTransactions table to mark it as "Returned"
    return_date = date.today().strftime("%Y-%m-%d")  # Get current date
    cursor.execute("UPDATE BorrowTransactions SET status = 'Returned', returnDate = ? WHERE borrowID = ?", 
                   (return_date, borrow_id))
    conn.commit()

    # Step 6: Remove the borrow record from the Borrow table
    cursor.execute("DELETE FROM Borrow WHERE email = ? AND itemID = ?", (email, item_id))
    conn.commit()

    # Step 7: Confirm success to the user
    cursor.execute("SELECT name FROM Item WHERE itemID = ?", (item_id,))
    item_name = cursor.fetchone()[0]

    print(f"\nSuccess! You returned '{item_name}'.")
    print(f"Return Date: {return_date}")


def donate_item():
    print("\n\n---------------------------------------")
    # Step 1: Ask for the full name, author, category, and genre
    full_name = input("\nEnter the full name of the item: ")
    author = input("\nEnter the author of the item: ")
    category = input("\nEnter the category of the item: ")
    genre = input("\nEnter the genre of the item: ")

    # Step 2: Set status to 'Available' (since it's a new donation)
    status = 'Available'

    # Step 3: Insert the new item into the Item table
    query = """INSERT INTO Item (name, author, category, genre, status)
               VALUES (?, ?, ?, ?, ?)"""
    cursor.execute(query, (full_name, author, category, genre, status))
    conn.commit()

    # Step 4: Confirm the donation
    print(f"\nSuccessfully donated the item: '{full_name}' by {author}.")
    print("It is now available in the library!")


def find_events():
    print("\n\n---------------------------------------")
    # Step 1: Perform SELECT * query to retrieve all events/items from the table
    query = "SELECT * FROM Events"  # Replace 'Event' with the actual table name
    cursor.execute(query)
    
    # Step 2: Fetch all rows from the query result
    events = cursor.fetchall()

    # Step 3: Check if any events exist in the table
    if not events:
        print("\nNo events found.")
        return

    # Step 4: Print headers (for readability, adjust based on your table columns)
    print("\nID | Event Name | Date | Location | Ages")  # Adjust based on your table columns
    print("-" * 50)  # A simple separator

    # Step 5: Iterate through each event and print its details
    for event in events:
        # Adjust the number of variables based on your table columns
        event_id, name, date, location, status = event  # Change column names based on your table schema
        print(f"{event_id} | {name} | {date} | {location} | {status}")
    
    print("-" * 50)  # Closing separator for the printed list

def register_event():
    print("\n\n---------------------------------------")
    email = input("\nEnter your email: ")

    # Step 1: Check if the email exists in the Member table
    cursor.execute("SELECT * FROM Member WHERE email = ?", (email,))
    member = cursor.fetchone()
    if not member:
        print("\nNo membership found with this email. Please create a membership first.")
        return

    # Step 2: Ask for the event ID
    event_id = input("\nEnter the Event ID you want to register for: ")

    # Step 3: Retrieve event details and room number
    cursor.execute("""
        SELECT e.name, e.scheduledTime, e.scheduledDate, e.targetAudience, l.roomNum 
        FROM Events e 
        LEFT JOIN Located l ON e.eventID = l.eventID 
        WHERE e.eventID = ?
    """, (event_id,))
    
    event = cursor.fetchone()

    # Step 4: Check if event exists
    if event is None:
        print("\nEvent not found.")
        return

    # Extract event details
    event_name, scheduled_time, scheduled_date, target_audience, room_num = event

    # Step 5: Display event details
    print("\nEvent Details:")
    print(f"Name: {event_name}")
    print(f"Scheduled Time: {scheduled_time}")
    print(f"Scheduled Date: {scheduled_date}")
    print(f"Target Audience: {target_audience}")
    print(f"Room Number: {room_num if room_num else 'Not assigned'}")

    # Step 6: Insert into Attends table
    try:
        cursor.execute("INSERT INTO Attends (email, eventID) VALUES (?, ?)", (email, event_id))
        conn.commit()
        print(f"\nSuccess! You are now registered for '{event_name}' At: {scheduled_time} On: {scheduled_date} In Room Number: {room_num}.")
    except sqlite3.IntegrityError:
        print("\nYou are already registered for this event.")



def volunteer_library():
    print("\nBecome a Library Volunteer!")

    # Validate email format
    while True:
        email = input("Enter your email: ")

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            print("\nInvalid email. Please enter a valid email address.")
            continue  # Restart email input

        # Check if email is already in the Member table
        cursor.execute("SELECT email FROM Member WHERE email = ?", (email,))
        if not cursor.fetchone():
            print("\nYou must be a registered library member to volunteer.")
            return  # Exit function if email is not in Member table

        # Check if the email is already a volunteer
        cursor.execute("SELECT email FROM Volunteer WHERE email = ?", (email,))
        if cursor.fetchone():
            print("\nYou are already registered as a volunteer.")
            return  # Exit function if the email is already a volunteer

        break  # If email is valid and not already a volunteer, proceed

    # Get today's date as the employment date
    employment_date = date.today().strftime("%Y-%m-%d")

    # Insert into Volunteer table
    query = '''INSERT INTO Volunteer (email, employmentDate) 
               VALUES (?, ?)'''
    cursor.execute(query, (email, employment_date))
    conn.commit()

    print(f"\nThank you! You are now registered as a library volunteer starting from {employment_date}.")





def user_question(option):
    print("\n\n---------------------------------------")
    if option == '1': 
        find_item()
    if option == '2':
        borrow_item()
    if option == '3':
        return_item()
    if option == '4':
        donate_item()
    if option == '5':
        find_events()
    if option == '6':
        register_event()
    if option == '7':
        volunteer_library()



# Check membership first before proceeding
membership_verified = check_membership()

if membership_verified:
    # Once the membership is verified or created, show the menu
    user_choice = introPage()

    while user_choice != '9':
        user_question(user_choice)
        user_choice = introPage()

    print('Thanks for using our library database, cya later nerd XD')

conn.close()