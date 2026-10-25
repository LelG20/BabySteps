"""Simple interactive CLI for the Transport Management System."""
from datetime import date, datetime
from pathlib import Path

from .models import Bus, Driver, Passenger, PaymentMethod, Route, VehicleStatus
from .system import TransportSystem

DATA_FILE = Path("transport_data.json")


def ask(prompt: str) -> str:
    return input(prompt).strip()


def run() -> None:
    system = TransportSystem.load(DATA_FILE) if DATA_FILE.exists() else TransportSystem()
    actions = {
        "1": ("Add passenger", lambda: add_passenger(system)),
        "2": ("Add driver", lambda: add_driver(system)),
        "3": ("Add bus", lambda: add_bus(system)),
        "4": ("Add route", lambda: add_route(system)),
        "5": ("Schedule trip", lambda: schedule_trip(system)),
        "6": ("List trips", lambda: list_trips(system)),
        "7": ("Book a seat", lambda: book_seat(system)),
        "8": ("List bookings", lambda: list_bookings(system)),
        "9": ("Pay for booking", lambda: pay_booking(system)),
        "10": ("Cancel booking", lambda: cancel_booking(system)),
    }
    print("Transport Management System")
    while True:
        print("\n" + "\n".join(f"{key}. {label}" for key, (label, _) in actions.items()))
        print("0. Save and exit")
        choice = ask("> ")
        if choice == "0":
            system.save(DATA_FILE)
            print(f"Saved system data to {DATA_FILE.resolve()}")
            return
        if choice not in actions:
            print("Choose a listed option.")
            continue
        try:
            actions[choice][1]()
            system.save(DATA_FILE)
        except (ValueError, KeyError) as exc:
            print(f"Could not complete that action: {exc}")


def add_passenger(system: TransportSystem) -> None:
    passenger = Passenger(ask("Passenger ID: "), ask("Full name: "),
                          ask("Phone number: "), ask("Email (optional): "))
    system.add_passenger(passenger)
    print(f"Added passenger {passenger.person_id}.")


def add_driver(system: TransportSystem) -> None:
    driver = Driver(ask("Driver ID: "), ask("Full name: "), ask("Phone number: "),
                    ask("Email (optional): "), ask("License number: "),
                    date.fromisoformat(ask("License expiry (YYYY-MM-DD): ")),
                    True, int(ask("Years of experience: ")))
    system.add_driver(driver)
    print(f"Added driver {driver.person_id}.")


def add_bus(system: TransportSystem) -> None:
    bus = Bus(ask("Vehicle ID: "), ask("Registration number: "), ask("Make: "),
              ask("Model: "), int(ask("Seat capacity: ")),
              float(ask("Current mileage (km): ") or "0"), VehicleStatus.AVAILABLE,
              ask("Air conditioning? (y/n): ").lower() == "y",
              float(ask("Luggage capacity (kg): ") or "0"))
    system.add_vehicle(bus)
    print(f"Added bus {bus.registration_number}.")


def add_route(system: TransportSystem) -> None:
    route = Route(ask("Route ID: "), ask("Origin: "), ask("Destination: "),
                  float(ask("Distance (km): ")), int(ask("Estimated duration (minutes): ")),
                  float(ask("Base fare: ")))
    system.add_route(route)
    print(f"Added route {route.origin} → {route.destination} ({route.route_id}).")


def schedule_trip(system: TransportSystem) -> None:
    departure = datetime.fromisoformat(ask("Departure (YYYY-MM-DD HH:MM): "))
    arrival = datetime.fromisoformat(ask("Arrival (YYYY-MM-DD HH:MM): "))
    trip = system.schedule_trip(ask("Route ID: "), ask("Vehicle ID: "), ask("Driver ID: "),
                                departure, arrival, trip_id=ask("Trip ID: "))
    print(f"Scheduled trip {trip.trip_id}.")


def list_trips(system: TransportSystem) -> None:
    if not system.trips:
        print("No trips scheduled.")
        return
    for trip in system.trips.values():
        route = system.routes[trip.route_id]
        available = len(system.available_seats(trip.trip_id))
        capacity = system.vehicles[trip.vehicle_id].seat_capacity
        print(f"{trip.trip_id} | {route.origin} → {route.destination} | "
              f"{trip.departure_time:%Y-%m-%d %H:%M} | {trip.status.value} | "
              f"seats {available}/{capacity} | fare {route.calculate_fare():.2f}")


def book_seat(system: TransportSystem) -> None:
    passenger_id, trip_id = ask("Passenger ID: "), ask("Trip ID: ")
    requested = ask("Seat number (blank for first available): ")
    booking = system.book_trip(passenger_id, trip_id, int(requested) if requested else None)
    print(f"Booking {booking.booking_id} confirmed: seat {booking.seat_number}, "
          f"fare {booking.total_amount:.2f}, ticket {booking.ticket.ticket_number}.")


def list_bookings(system: TransportSystem) -> None:
    if not system.bookings:
        print("No bookings yet.")
        return
    for booking in system.bookings.values():
        passenger = system.passengers[booking.passenger_id]
        print(f"{booking.booking_id} | {passenger.full_name} | trip {booking.trip_id} | "
              f"seat {booking.seat_number} | {booking.status.value} | "
              f"{booking.total_amount:.2f}")


def pay_booking(system: TransportSystem) -> None:
    booking_id = ask("Booking ID: ")
    print("Payment methods: " + ", ".join(method.value for method in PaymentMethod))
    method = PaymentMethod(ask("Method: ").lower())
    payment = system.process_payment(booking_id, method)
    print(f"Payment {payment.payment_id} received ({payment.amount:.2f}, {method.value}).")


def cancel_booking(system: TransportSystem) -> None:
    booking = system.cancel_booking(ask("Booking ID: "))
    print(f"Booking {booking.booking_id} cancelled. Paid amounts were refunded where applicable.")
