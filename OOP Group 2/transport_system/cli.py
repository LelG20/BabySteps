"""Console menu for the CSV-based transport management system."""
from datetime import date, datetime, timedelta

from .models import (
    Bus, Dispatcher, Driver, Fleet, MaintenanceRecord, Minibus, Passenger,
    Route, Stop,
)
from .csv_storage import DEFAULT_DATA_FOLDER
from .system import TransportSystem


def _yes(value):
    return value.strip().lower() in ("yes", "y", "true", "1")


def _show_records(system):
    print("\nFLEETS")
    for fleet in system.fleets.values():
        print(fleet.fleet_id, fleet.fleet_name,
              "Vehicles:", fleet.get_fleet_size())

    print("\nVEHICLES")
    for vehicle in system.vehicles.values():
        print(vehicle.vehicle_id, vehicle.get_vehicle_type(),
              vehicle.registration_number, vehicle.status.value,
              "Seats:", vehicle.seat_capacity)

    print("\nPASSENGERS")
    for passenger in system.passengers.values():
        print(passenger.person_id, passenger.full_name,
              "Loyalty points:", passenger.loyalty_points)

    print("\nDRIVERS")
    for driver in system.drivers.values():
        print(driver.person_id, driver.full_name,
              "Available:", driver.availability_status,
              "License valid:", driver.is_license_valid())

    print("\nDISPATCHERS")
    for dispatcher in system.dispatchers.values():
        print(dispatcher.person_id, dispatcher.full_name, dispatcher.shift)

    print("\nROUTES")
    for route in system.routes.values():
        print(route.route_id, route.origin, "to", route.destination,
              "Stops:", len(route.get_stops()), "Fare:", route.calculate_fare())

    print("\nTRIPS")
    for trip in system.trips.values():
        print(trip.trip_id, trip.route_id, trip.status.value,
              trip.departure_time.isoformat(timespec="minutes"))

    print("\nBOOKINGS")
    for booking in system.bookings.values():
        print(booking.booking_id, "Passenger:", booking.passenger_id,
              "Trip:", booking.trip_id, "Seat:", booking.seat_number,
              "Status:", booking.status.value)

    print("\nPAYMENTS:", len(system.payments))
    print("MAINTENANCE RECORDS:", len(system.maintenance_records))


def run():
    # Load the prefilled or previously saved CSV files.
    system = TransportSystem.load()
    print("Transport Management System")
    print("CSV folder:", DEFAULT_DATA_FOLDER)
    print("Successful changes are saved automatically.")
    print("Choose 12 to view the loaded records.")

    while True:
        print("\n1. Add fleet")
        print("2. Add bus")
        print("3. Add minibus")
        print("4. Add passenger")
        print("5. Add driver")
        print("6. Add dispatcher")
        print("7. Add route")
        print("8. Schedule trip")
        print("9. List trips")
        print("10. Start or complete a trip")
        print("11. Cancel a booking")
        print("12. View all loaded records")
        print("13. Add a maintenance record")
        print("14. Complete maintenance")
        print("15. Record a driver issue")
        print("16. Show a dispatcher's report")
        print("0. Save CSV files and exit")
        choice = input("> ").strip()

        try:
            if choice == "1":
                fleet = Fleet(
                    input("Fleet ID: "),
                    input("Name: "),
                    input("Depot: "),
                )
                system.add_fleet(fleet)
                print("Fleet added.")

            elif choice == "2":
                bus = Bus(
                    input("Bus ID: "),
                    input("Registration: "),
                    input("Make: "),
                    input("Model: "),
                    int(input("Seat capacity: ")),
                    has_air_conditioning=_yes(input("Air conditioning? (yes/no): ")),
                    luggage_capacity_kg=float(input("Luggage capacity in kg: ")),
                )
                system.add_vehicle(bus, input("Fleet ID: "))
                print("Bus added to fleet.")

            elif choice == "3":
                minibus = Minibus(
                    input("Minibus ID: "),
                    input("Registration: "),
                    input("Make: "),
                    input("Model: "),
                    int(input("Seat capacity: ")),
                    permit_number=input("Permit number: "),
                    is_city_route=_yes(input("City route? (yes/no): ")),
                )
                system.add_vehicle(minibus, input("Fleet ID: "))
                print("Minibus added to fleet.")

            elif choice == "4":
                passenger = Passenger(
                    input("Passenger ID: "),
                    input("Name: "),
                    input("Phone: "),
                    email=input("Email (optional): "),
                )
                system.add_passenger(passenger)
                print("Passenger added.")

            elif choice == "5":
                driver = Driver(
                    input("Driver ID: "),
                    input("Name: "),
                    input("Phone: "),
                    license_number=input("License number: "),
                    license_expiry=date.fromisoformat(
                        input("License expiry (YYYY-MM-DD): ")
                    ),
                    years_experience=int(input("Years of experience: ")),
                )
                system.add_driver(driver)
                print("Driver added.")

            elif choice == "6":
                dispatcher = Dispatcher(
                    input("Dispatcher ID: "),
                    input("Name: "),
                    input("Phone: "),
                    employee_id=input("Employee ID: "),
                    shift=input("Shift: "),
                )
                system.add_dispatcher(dispatcher)
                print("Dispatcher added.")

            elif choice == "7":
                route_id = input("Route ID: ")
                origin = input("Origin: ")
                destination = input("Destination: ")
                first_stop = Stop(route_id + "-STOP-1", origin + " Terminal", origin)
                last_stop = Stop(route_id + "-STOP-2", destination + " Terminal", destination)
                route = Route(
                    route_id, origin, destination,
                    float(input("Distance in km: ")),
                    int(input("Estimated duration in minutes: ")),
                    float(input("Base fare: ")),
                    [first_stop, last_stop],
                )
                system.add_route(route)
                print("Route added with two stops.")

            elif choice == "8":
                route_id = input("Route ID: ")
                vehicle_id = input("Vehicle ID: ")
                driver_id = input("Driver ID: ")
                dispatcher_id = input("Dispatcher ID: ")
                departure = datetime.now() + timedelta(days=1)
                arrival = departure + timedelta(hours=2)
                trip = system.schedule_trip(
                    route_id, vehicle_id, driver_id, departure, arrival,
                    dispatcher_id,
                )
                print("Trip added:", trip.trip_id)
                print("Departure:", trip.departure_time.isoformat(timespec="minutes"))

            elif choice == "9":
                if not system.trips:
                    print("No trips have been added.")
                for trip in system.trips.values():
                    route = system.routes[trip.route_id]
                    print(trip.trip_id, route.origin, "to", route.destination,
                          trip.status.value)

            elif choice == "10":
                trip_id = input("Trip ID: ")
                action = input("Type 'start' or 'complete': ").strip().lower()
                if action == "start":
                    system.start_trip(trip_id)
                elif action == "complete":
                    system.complete_trip(trip_id)
                else:
                    raise ValueError("Choose 'start' or 'complete'.")
                print("Trip status updated.")

            elif choice == "11":
                booking_id = input("Booking ID: ")
                system.cancel_booking(booking_id)
                print("Booking cancelled. Any completed payment was refunded.")

            elif choice == "12":
                _show_records(system)

            elif choice == "13":
                record = MaintenanceRecord(
                    input("Record ID: "),
                    input("Vehicle ID: "),
                    date.fromisoformat(input("Service date (YYYY-MM-DD): ")),
                    input("Description: "),
                    float(input("Cost: ")),
                    date.fromisoformat(input("Next service date (YYYY-MM-DD): ")),
                )
                record.schedule_service()
                system.add_maintenance_record(record)
                print("Maintenance record added; vehicle marked for maintenance.")

            elif choice == "14":
                record_id = input("Maintenance record ID: ")
                system.complete_maintenance(record_id)
                print("Maintenance completed.")

            elif choice == "15":
                driver_id = input("Driver ID: ")
                issue = input("Issue description: ")
                system.drivers[driver_id].report_issue(issue)
                print("Driver issue recorded.")

            elif choice == "16":
                dispatcher_id = input("Dispatcher ID: ")
                dispatcher = system.dispatchers[dispatcher_id]
                print(dispatcher.generate_report(system))

            elif choice == "0":
                system.save()
                print("CSV files saved. Goodbye.")
                break

            else:
                print("Please choose a number from the menu.")

            if choice in ("1", "2", "3", "4", "5", "6", "7", "8",
                          "10", "11", "13", "14", "15"):
                system.save()
                print("Changes saved to:", DEFAULT_DATA_FOLDER)

        except (ValueError, KeyError) as error:
            print("Could not complete that action:", error)


if __name__ == "__main__":
    run()
