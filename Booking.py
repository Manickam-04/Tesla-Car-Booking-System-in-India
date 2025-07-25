# This code is sample code of a Tesla car booking system in India.
# It allows users to view available cars, book a car, view bookings, and cancel bookings

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
        print("\nProcessing Debit/Credit Card Payment...")
        card_no = input("Enter Card Number (XXXX-XXXX-XXXX-XXXX): ")
        name = input("Card Holder Name: ")
        print("Processing Card Payment...")
        payment_method = "Debit/Credit Card"
        emi_months = None
        amount = car_price

    elif choice == "2":
        print("\nProcessing UPI Payment...")
        print("Please ensure your UPI ID is linked to your bank account.")
        upi_id = input("Enter UPI ID (e.g., name@upi): ")
        print("Processing UPI Payment...")
        payment_method = "UPI"
        emi_months = None
        amount = car_price

    elif choice == "3":
        print("\nProcessing Loan Installment (EMI) Payment...")
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
    print("""Full Self-Driving Capability
In future updates, your car will be able to drive itself almost anywhere with minimal driver intervention
          For that you need to pay ₹6,00,000 extra.""")
    full_self_driving = input("Do you want to add FSD?(✅/❌) or (yes/no):")
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
        cursor.execute("select booking_id from bookings where customer_name=%s and phone=%s and state=%s and car_id=%s", (name, phone, state, car_id))
        car_booking = cursor.fetchone()

        booking_id = cursor.lastrowid
        car_price = car_data[1]
        if full_self_driving.lower() == 'yes' or full_self_driving.lower() == '✅':
            car_price += 600000  
            print("Full Self-Driving Capability added for ₹6,00,000.")

        cursor.execute("UPDATE cars SET available = available - 1 WHERE id = %s", (car_id,))
        conn.commit()

        print(f"\n Booking Successful! Booking ID: {car_booking[0]}")
        process_payment(booking_id, car_price)
    else:
        print("\n Car Not Available!")

def view_bookings():
    bch= int(input("Enter your Booking ID to view details:"))
    cursor.execute("""
        SELECT b.booking_id, b.customer_name, b.phone, b.state, c.model_name, p.payment_method, p.amount, b.booking_date
        FROM bookings b
        JOIN cars c ON b.car_id = c.id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
    """)
    bookings = cursor.fetchall()
    found = False
    for b in bookings:
        payment_method = b[5] or "Not Paid"
        amount = f"₹{b[6]:,.2f}" if b[6] else "N/A"

        if b[0] == bch: 
            found = True
            print("\n-----Your Booking Details----")
            print(f"Booking ID: {b[0]}")
            print(f"Customer Name: {b[1]}")
            print(f"Phone: {b[2]}")
            print(f"State: {b[3]}")
            print(f"Car Model: {b[4]}")
            print(f"Payment Method: {payment_method}")
            print(f"Amount: {amount}")
            print(f"Booking Date and Time: {b[7]}")
    if not found:
        print("\n No booking found with this ID.")

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

    print(f"Booking ID {booking_id} has been cancelled and payment will be refunded through the original payment method.")

def main():
    while True:
        print("\n===== Tesla Car Booking System (India) =====")
        print("1. View Cars")
        print("2. Book a Car")
        print("3. View my Booking")
        print("4. Cancel Booking")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            view_cars()
        elif choice == "2":
            book_car()
        elif choice == "3":
            view_bookings()
        elif choice == "4":
            cancel_booking()
        elif choice == "5":
            print("Exiting... Thank you for showing interest in Tesla India!")
            break
        else:
            print("Invalid choice! Try again.")

main()

cursor.close()
conn.close()
