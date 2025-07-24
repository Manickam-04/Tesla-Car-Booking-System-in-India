import mysql.connector
import math

conn = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="jeevitha",  
    database="tesla"
)
cursor = conn.cursor()

def view_cars():
    cursor.execute("SELECT * FROM cars")
    cars = cursor.fetchall()
    print("\nAvailable Tesla Cars in India:")
    print("ID | Model Name | Price (INR) | Available Units")
    print("----------------------------------------------")
    for car in cars:
        print(f"{car[0]} | {car[1]} | ₹{car[2]:,.2f} | {car[3]}")
    print("\nCar-1: Model Y |Range: 500 km | Top Speed: 201 km/h | 0-100 km/h in 5.9 sec | available in 6 colors | Rear Wheel Drive")
    print("\nCar-2: Model Y (Long Range) |Range: 622 km | Top Speed: 201 km/h | 0-100 km/h in 5.6 sec | available in 6 colors | Rear Wheel Drive")
    print("\nFully-Automatic Driving will be unlock in future updates for all Tesla cars in India.")

def process_payment(booking_id, car_price):
    print("\nChoose Payment Method:")
    print("1. Debit/Credit Card")
    print("2. UPI")
    print("3. Loan Installment (EMI)")

    choice = input("Enter choice: ")

    if choice == "1":
        card_no = input("Enter Card Number (XXXX-XXXX-XXXX-XXXX): ")
        name = input("Card Holder Name: ")
        print("Processing Card Payment...")
        payment_method = "Debit/Credit Card"
        emi_months = None
        amount = car_price

    elif choice == "2":
        upi_id = input("Enter UPI ID (e.g., name@upi): ")
        print("Processing UPI Payment...")
        payment_method = "UPI"
        emi_months = None
        amount = car_price

    elif choice == "3":
        emi_months = int(input("Enter EMI duration (6, 12, 24 months): "))
        interest_rate = 0.10  
        monthly_interest = interest_rate / 12
        emi = (car_price * monthly_interest * math.pow(1 + monthly_interest, emi_months)) / \
              (math.pow(1 + monthly_interest, emi_months) - 1)
        print(f"EMI Plan Approved: ₹{emi:,.2f} per month for {emi_months} months")
        payment_method = "Loan EMI"
        amount = emi * emi_months

    else:
        print("Invalid payment method!")
        return

    cursor.execute("""
        INSERT INTO payments (booking_id, payment_method, amount, emi_months)
        VALUES (%s, %s, %s, %s)
    """, (booking_id, payment_method, amount, emi_months))
    conn.commit()

    print(f"Payment Successful via {payment_method} for ₹{amount:,.2f}")

def book_car():
    view_cars()
    car_id = int(input("\nEnter Car ID to book: "))
    name = input("Enter Your Name: ")
    phone = input("Enter Phone Number: ")
    state = input("Enter Registration State: ")

    cursor.execute("SELECT available, price FROM cars WHERE id=%s", (car_id,))
    car_data = cursor.fetchone()

    if car_data and car_data[0] > 0:
        cursor.execute(
            "INSERT INTO bookings (customer_name, phone, state, car_id) VALUES (%s, %s, %s, %s)",
            (name, phone, state, car_id)
        )
        conn.commit()

        booking_id = cursor.lastrowid
        car_price = car_data[1]

        cursor.execute("UPDATE cars SET available = available - 1 WHERE id = %s", (car_id,))
        conn.commit()

        print("\n Booking Successful!")
        process_payment(booking_id, car_price)
    else:
        print("\n Car Not Available!")

def view_bookings():
    cursor.execute("""
        SELECT b.booking_id, b.customer_name, b.phone, b.state, c.model_name, p.payment_method, p.amount, b.booking_date
        FROM bookings b
        JOIN cars c ON b.car_id = c.id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
    """)
    bookings = cursor.fetchall()

    print("\nAll Bookings & Payments:")
    print("  ID |   Customer   | Phone | State |   Car Model   |   Payment   |   Amount   |   Date and Time  ")
    print("--------------------------------------------------------------------------------------------------")
    for b in bookings:
        print(f"{b[0]} | {b[1]} | {b[2]} | {b[3]} | {b[4]} | {b[5]} ₹{b[6]:,.2f} | {b[7]}")

def cancel_booking():
    booking_id = int(input("\nEnter Booking ID to Cancel: "))
    cursor.execute("SELECT car_id FROM bookings WHERE booking_id=%s", (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        print("Booking ID not found!")
        return

    car_id = booking[0]

    cursor.execute("DELETE FROM payments WHERE booking_id=%s", (booking_id,))
    conn.commit()

    cursor.execute("DELETE FROM bookings WHERE booking_id=%s", (booking_id,))
    conn.commit()

    cursor.execute("UPDATE cars SET available = available + 1 WHERE id=%s", (car_id,))
    conn.commit()

    print(f"Booking ID {booking_id} has been cancelled and payment will be refunded.")

def main():
    while True:
        print("\n===== Tesla Car Booking System (India) =====")
        print("1. View Cars")
        print("2. Book a Car")
        print("3. View All Bookings & Payments")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            view_cars()
        elif choice == "2":
            book_car()
        elif choice == "3":
            view_bookings()
        elif choice == "4":
            print("Exiting... Thank you for booking with Tesla India!")
            break
        else:
            print("Invalid choice! Try again.")

main()

cursor.close()
conn.close()
