"""Customer menu for browsing and booking available trips."""
from uuid import uuid4

from .models import (
    BookingStatus, Passenger, PaymentMethod, PaymentStatus, TripStatus,
)
from .csv_storage import DEFAULT_DATA_FOLDER
from .system import TransportSystem


def get_available_trips(system):
    """Return scheduled trips that still have at least one free seat."""
    trips = []
    for trip in system.trips.values():
        if trip.status == TripStatus.SCHEDULED:
            if system.available_seats(trip.trip_id):
                trips.append(trip)
    return trips


def find_passenger_by_phone(system, phone_number):
    phone_number = phone_number.strip()
    for passenger in system.passengers.values():
        if passenger.phone_number.strip() == phone_number:
            return passenger
    return None


def get_or_create_passenger(system, full_name, phone_number, email=""):
    full_name = full_name.strip()
    phone_number = phone_number.strip()
    if not full_name or not phone_number:
        raise ValueError("Name and phone number are required.")

    existing = find_passenger_by_phone(system, phone_number)
    if existing is not None:
        return existing

    person_id = "CUST-" + uuid4().hex[:8].upper()
    while person_id in system.passengers:
        person_id = "CUST-" + uuid4().hex[:8].upper()

    passenger = Passenger(
        person_id, full_name, phone_number, email=email.strip()
    )
    system.add_passenger(passenger)
    return passenger


def _show_available_trips(system):
    trips = get_available_trips(system)
    if not trips:
        print("There are no scheduled trips with available seats.")
        return trips

    print("\nAVAILABLE TRIPS")
    for trip in trips:
        route = system.routes[trip.route_id]
        seats = system.available_seats(trip.trip_id)
        print(
            trip.trip_id, "|", route.origin, "to", route.destination,
            "|", trip.departure_time.strftime("%Y-%m-%d %H:%M"),
            "| Fare:", route.calculate_fare(),
            "| Seats left:", len(seats),
        )
    return trips


def _book_a_trip(system):
    trips = _show_available_trips(system)
    if not trips:
        return

    trip_id = input("Trip ID to book: ").strip()
    trip = system.trips.get(trip_id)
    if trip not in trips:
        raise ValueError("Choose a trip from the available trips shown above.")

    full_name = input("Your full name: ")
    phone_number = input("Your phone number: ")
    email = input("Email (optional): ")
    passenger = get_or_create_passenger(
        system, full_name, phone_number, email
    )

    seats = system.available_seats(trip_id)
    print("Available seat numbers:", ", ".join(str(seat) for seat in seats))
    seat_text = input("Seat number (leave blank for the first available): ").strip()
    seat_number = int(seat_text) if seat_text else None

    booking = system.book_trip(passenger.person_id, trip_id, seat_number)
    print("Booking confirmed.")
    print("Passenger ID:", passenger.person_id)
    print("Booking ID:", booking.booking_id)
    print("Seat:", booking.seat_number)
    print("Fare:", booking.calculate_total())
    print("Ticket:", booking.ticket.ticket_number)


def _my_bookings(system):
    phone_number = input("Phone number used for the booking: ").strip()
    passenger = find_passenger_by_phone(system, phone_number)
    if passenger is None:
        print("No customer was found with that phone number.")
        return

    found = False
    print("\nYOUR BOOKINGS")
    for booking in system.bookings.values():
        if booking.passenger_id != passenger.person_id:
            continue
        found = True
        payment_status = "unpaid"
        for payment in system.payments.values():
            if payment.booking_id == booking.booking_id:
                payment_status = payment.status.value
        ticket_number = booking.ticket.ticket_number if booking.ticket else "None"
        print(
            booking.booking_id, "| Trip:", booking.trip_id,
            "| Seat:", booking.seat_number,
            "| Booking:", booking.status.value,
            "| Payment:", payment_status,
            "| Ticket:", ticket_number,
        )
    if not found:
        print("No bookings were found for this customer.")


def _pay_for_booking(system):
    phone_number = input("Phone number used for the booking: ").strip()
    passenger = find_passenger_by_phone(system, phone_number)
    if passenger is None:
        raise ValueError("No customer was found with that phone number.")

    paid_booking_ids = set()
    for payment in system.payments.values():
        if payment.status == PaymentStatus.PAID:
            paid_booking_ids.add(payment.booking_id)

    bookings = []
    for booking in system.bookings.values():
        if (booking.passenger_id == passenger.person_id
                and booking.status == BookingStatus.CONFIRMED
                and booking.booking_id not in paid_booking_ids):
            bookings.append(booking)

    if not bookings:
        print("You have no confirmed, unpaid bookings.")
        return

    print("Your unpaid bookings:")
    for booking in bookings:
        print(booking.booking_id, "Trip:", booking.trip_id,
              "Seat:", booking.seat_number, "Fare:", booking.total_amount)

    booking_id = input("Booking ID to pay for: ").strip()
    if not any(booking.booking_id == booking_id for booking in bookings):
        raise ValueError("Choose one of your unpaid bookings.")

    print("1. M-Pesa  2. Card  3. Cash")
    method_choice = input("Payment method: ").strip()
    methods = {
        "1": PaymentMethod.MPESA,
        "2": PaymentMethod.CARD,
        "3": PaymentMethod.CASH,
    }
    if method_choice not in methods:
        raise ValueError("Choose 1, 2, or 3.")

    payment = system.process_payment(booking_id, methods[method_choice])
    print("Payment recorded:", payment.status.value)
    print("This is a local demonstration record; no real payment was taken.")


def _cancel_my_booking(system):
    phone_number = input("Phone number used for the booking: ").strip()
    passenger = find_passenger_by_phone(system, phone_number)
    if passenger is None:
        raise ValueError("No customer was found with that phone number.")

    booking_id = input("Booking ID to cancel: ").strip()
    booking = system.bookings.get(booking_id)
    if booking is None or booking.passenger_id != passenger.person_id:
        raise ValueError("That booking does not belong to this customer.")

    system.cancel_booking(booking_id)
    print("Booking cancelled. Any completed payment was marked as refunded.")


def run():
    # Customers use the same CSV records as the management application.
    system = TransportSystem.load()
    print("Transport Management System - Customer Booking")
    print("CSV folder:", DEFAULT_DATA_FOLDER)
    print("Successful bookings, payments, and cancellations are saved automatically.")
    print("Browse scheduled trips, book seats, and manage your own bookings.")

    while True:
        print("\n1. Browse available trips")
        print("2. Book a trip")
        print("3. View my bookings")
        print("4. Pay for my booking")
        print("5. Cancel my booking")
        print("0. Save CSV files and exit")
        choice = input("> ").strip()

        try:
            if choice == "1":
                _show_available_trips(system)
            elif choice == "2":
                _book_a_trip(system)
            elif choice == "3":
                _my_bookings(system)
            elif choice == "4":
                _pay_for_booking(system)
            elif choice == "5":
                _cancel_my_booking(system)
            elif choice == "0":
                system.save()
                print("CSV files saved. Goodbye.")
                break
            else:
                print("Please choose a number from the menu.")

            if choice in ("2", "4", "5"):
                system.save()
                print("Changes saved to:", DEFAULT_DATA_FOLDER)
        except (ValueError, KeyError) as error:
            print("Could not complete that action:", error)


if __name__ == "__main__":
    run()
