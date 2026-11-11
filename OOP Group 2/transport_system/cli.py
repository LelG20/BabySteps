"""Console menu for the transport management system."""
from datetime import date, datetime, timedelta

from .models import Bus, Dispatcher, Driver, Fleet, Passenger, PaymentMethod, Route, Stop
from .system import TransportSystem


# ==================== PRESENTER: Maryhope ====================
# This menu collects simple input and sends it to the system coordinator.
def run():
    system = TransportSystem.load("transport_data.json")
    print("Transport Management System")

    while True:
        print("\n1. Add fleet")
        print("2. Add bus")
        print("3. Add passenger")
        print("4. Add driver")
        print("5. Add dispatcher")
        print("6. Add route")
        print("7. Schedule trip")
        print("8. Book a seat")
        print("9. Pay for a booking")
        print("10. List trips")
        print("11. Start or complete a trip")
        print("12. Cancel a booking")
        print("0. Save and exit")
        choice = input("> ").strip()

        try:
            if choice == "1":
                fleet = Fleet(input("Fleet ID: "), input("Name: "), input("Depot: "))
                system.add_fleet(fleet)
                print("Fleet added.")

            elif choice == "2":
                bus = Bus(
                    input("Bus ID: "), input("Registration: "),
                    input("Make: "), input("Model: "),
                    int(input("Seat capacity: ")),
                )
                system.add_vehicle(bus, input("Fleet ID: "))
                print("Bus added to fleet.")

            elif choice == "3":
                passenger = Passenger(
                    input("Passenger ID: "), input("Name: "), input("Phone: ")
                )
                system.add_passenger(passenger)
                print("Passenger added.")

            elif choice == "4":
                driver = Driver(
                    input("Driver ID: "), input("Name: "), input("Phone: "),
                    license_number=input("License number: "),
                    license_expiry=date.today() + timedelta(days=365),
                )
                system.add_driver(driver)
                print("Driver added.")

            elif choice == "5":
                dispatcher = Dispatcher(
                    input("Dispatcher ID: "), input("Name: "), input("Phone: "),
                    employee_id=input("Employee ID: "),
                    shift=input("Shift: "),
                )
                system.add_dispatcher(dispatcher)
                print("Dispatcher added.")

            elif choice == "6":
                route_id = input("Route ID: ")
                origin = input("Origin: ")
                destination = input("Destination: ")
                first_stop = Stop("STOP-1", origin + " Terminal", origin)
                last_stop = Stop("STOP-2", destination + " Terminal", destination)
                route = Route(route_id, origin, destination, 100, 120, 850,
                              [first_stop, last_stop])
                system.add_route(route)
                print("Route added with two stops.")

            elif choice == "7":
                route_id = input("Route ID: ")
                vehicle_id = input("Bus ID: ")
                driver_id = input("Driver ID: ")
                dispatcher_id = input("Dispatcher ID: ")
                start = datetime.now() + timedelta(days=1)
                end = start + timedelta(hours=2)
                trip = system.schedule_trip(route_id, vehicle_id, driver_id,
                                            start, end, dispatcher_id)
                print("Trip added:", trip.trip_id)

            elif choice == "8":
                passenger_id = input("Passenger ID: ")
                trip_id = input("Trip ID: ")
                booking = system.book_trip(passenger_id, trip_id)
                print("Booking confirmed:", booking.booking_id)
                print("Seat:", booking.seat_number, "Fare:", booking.total_amount)

            elif choice == "9":
                booking_id = input("Booking ID: ")
                print("1. M-Pesa  2. Card  3. Cash")
                method_choice = input("Payment method: ")
                methods = {"1": PaymentMethod.MPESA,
                           "2": PaymentMethod.CARD,
                           "3": PaymentMethod.CASH}
                payment = system.process_payment(booking_id, methods[method_choice])
                print("Payment recorded:", payment.status.value)

            elif choice == "10":
                for trip in system.trips.values():
                    print(trip.trip_id, trip.route_id, trip.status.value)

            elif choice == "11":
                trip_id = input("Trip ID: ")
                action = input("Type 'start' or 'complete': ").strip().lower()
                if action == "start":
                    system.start_trip(trip_id)
                elif action == "complete":
                    system.complete_trip(trip_id)
                else:
                    raise ValueError("Choose 'start' or 'complete'.")
                print("Trip status updated.")

            elif choice == "12":
                booking_id = input("Booking ID: ")
                system.cancel_booking(booking_id)
                print("Booking cancelled.")

            elif choice == "0":
                system.save("transport_data.json")
                print("Data saved. Goodbye.")
                break

            else:
                print("Please choose a number from the menu.")
        except (ValueError, KeyError) as error:
            print("Could not complete that action:", error)


if __name__ == "__main__":
    run()
