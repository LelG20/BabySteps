"""Application rules for the transport management system."""
from datetime import datetime
from uuid import uuid4

from .csv_storage import CSVStorage
from .models import (
    Booking, BookingStatus, Bus, Driver, Dispatcher, Fleet, MaintenanceRecord,
    Minibus, Passenger, Payment, PaymentMethod, PaymentStatus, Route, Ticket,
    Trip, TripStatus, Vehicle, VehicleStatus,
)


def _new_id(prefix):
    return prefix + "-" + uuid4().hex[:6].upper()


# The system keeps the main collections and connects the objects.
class TransportSystem:
    def __init__(self):
        self.passengers = {}
        self.drivers = {}
        self.dispatchers = {}
        self.vehicles = {}
        self.routes = {}
        self.fleets = {}
        self.trips = {}
        self.bookings = {}
        self.payments = {}
        self.maintenance_records = {}

    def add_passenger(self, passenger: Passenger):
        if passenger.person_id in self.passengers:
            raise ValueError("Passenger ID already exists.")
        self.passengers[passenger.person_id] = passenger

    def add_driver(self, driver: Driver):
        if driver.person_id in self.drivers:
            raise ValueError("Driver ID already exists.")
        self.drivers[driver.person_id] = driver

    def add_dispatcher(self, dispatcher: Dispatcher):
        if dispatcher.person_id in self.dispatchers:
            raise ValueError("Dispatcher ID already exists.")
        self.dispatchers[dispatcher.person_id] = dispatcher

    def add_fleet(self, fleet: Fleet):
        if fleet.fleet_id in self.fleets:
            raise ValueError("Fleet ID already exists.")
        self.fleets[fleet.fleet_id] = fleet

    def add_route(self, route: Route):
        if route.route_id in self.routes:
            raise ValueError("Route ID already exists.")
        self.routes[route.route_id] = route

    def add_vehicle(self, vehicle: Vehicle, fleet_id: str):
        if fleet_id not in self.fleets:
            raise ValueError("Fleet was not found.")
        for fleet in self.fleets.values():
            if vehicle.vehicle_id in fleet.vehicle_ids:
                raise ValueError("Vehicle already belongs to a fleet.")
        if vehicle.vehicle_id in self.vehicles:
            raise ValueError("Vehicle ID already exists.")
        self.vehicles[vehicle.vehicle_id] = vehicle
        self.fleets[fleet_id].add_vehicle(vehicle)

    def schedule_trip(self, route_id: str, vehicle_id: str, driver_id: str,
                      departure_time: datetime, arrival_time: datetime,
                      dispatcher_id: str, trip_id: str | None = None):
        if route_id not in self.routes:
            raise ValueError("Route was not found.")
        if vehicle_id not in self.vehicles:
            raise ValueError("Vehicle was not found.")
        if driver_id not in self.drivers:
            raise ValueError("Driver was not found.")
        if dispatcher_id not in self.dispatchers:
            raise ValueError("Dispatcher was not found.")
        if arrival_time <= departure_time:
            raise ValueError("Trip arrival must be later than departure.")

        vehicle = self.vehicles[vehicle_id]
        driver = self.drivers[driver_id]
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise ValueError("Vehicle is not available for scheduling.")
        if not driver.availability_status:
            raise ValueError("Driver is not available for scheduling.")
        if not driver.is_license_valid(departure_time.date()):
            raise ValueError("The driver's license is missing or expired.")

        for existing in self.trips.values():
            if existing.status not in (TripStatus.SCHEDULED, TripStatus.IN_PROGRESS):
                continue
            overlaps = (departure_time < existing.arrival_time
                        and existing.departure_time < arrival_time)
            if overlaps and existing.vehicle_id == vehicle_id:
                raise ValueError("Vehicle has an overlapping trip.")
            if overlaps and existing.driver_id == driver_id:
                raise ValueError("Driver has an overlapping trip.")

        if trip_id and trip_id in self.trips:
            raise ValueError("Trip ID already exists.")

        trip = Trip(
            trip_id or _new_id("TRIP"), route_id, vehicle_id, driver_id,
            departure_time, arrival_time, dispatcher_id,
        )
        self.trips[trip.trip_id] = trip
        return trip

    def available_seats(self, trip_id: str) -> list[int]:
        trip = self.trips[trip_id]
        vehicle = self.vehicles[trip.vehicle_id]
        occupied = []
        for booking in self.bookings.values():
            if (booking.trip_id == trip_id
                    and booking.status == BookingStatus.CONFIRMED):
                occupied.append(booking.seat_number)

        seats = []
        for number in range(1, vehicle.seat_capacity + 1):
            if number not in occupied:
                seats.append(number)
        return seats

    def book_trip(self, passenger_id: str, trip_id: str,
                  seat_number: int | None = None):
        if passenger_id not in self.passengers:
            raise ValueError("Passenger was not found.")
        if trip_id not in self.trips:
            raise ValueError("Trip was not found.")

        trip = self.trips[trip_id]
        if trip.status != TripStatus.SCHEDULED:
            raise ValueError("Only scheduled trips can be booked.")

        free_seats = self.available_seats(trip_id)
        if not free_seats:
            raise ValueError("There are no seats left.")
        if seat_number is None:
            seat_number = free_seats[0]
        if seat_number not in free_seats:
            raise ValueError("That seat is already taken or not valid.")

        fare = self.routes[trip.route_id].calculate_fare()
        ticket = Ticket()
        ticket.generate_ticket()
        booking = Booking(
            _new_id("BOOKING"), passenger_id, trip_id, datetime.now(),
            seat_number, fare, ticket=ticket,
        )
        booking.confirm()
        self.bookings[booking.booking_id] = booking
        return booking

    def cancel_booking(self, booking_id: str):
        if booking_id not in self.bookings:
            raise ValueError("Booking was not found.")
        booking = self.bookings[booking_id]
        booking.cancel()
        for payment in self.payments.values():
            if payment.booking_id == booking_id:
                payment.refund()
        return booking

    def process_payment(self, booking_id: str, method: PaymentMethod):
        if booking_id not in self.bookings:
            raise ValueError("Booking was not found.")
        booking = self.bookings[booking_id]
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError("A cancelled booking cannot be paid for.")
        for payment in self.payments.values():
            if (payment.booking_id == booking_id
                    and payment.status == PaymentStatus.PAID):
                raise ValueError("This booking already has a completed payment.")

        payment = Payment(
            _new_id("PAYMENT"), booking_id, booking.total_amount, method
        )
        if not payment.process_payment():
            raise ValueError("Payment amount must be greater than zero.")
        self.payments[payment.payment_id] = payment
        self.passengers[booking.passenger_id].loyalty_points += int(payment.amount)
        return payment

    def start_trip(self, trip_id: str):
        if trip_id not in self.trips:
            raise ValueError("Trip was not found.")
        trip = self.trips[trip_id]
        if self.vehicles[trip.vehicle_id].status != VehicleStatus.AVAILABLE:
            raise ValueError("Vehicle is not available to start this trip.")
        if not self.drivers[trip.driver_id].availability_status:
            raise ValueError("Driver is not available to start this trip.")

        trip.start()
        self.vehicles[trip.vehicle_id].update_status(VehicleStatus.IN_SERVICE)
        self.drivers[trip.driver_id].availability_status = False
        return trip

    def complete_trip(self, trip_id: str):
        if trip_id not in self.trips:
            raise ValueError("Trip was not found.")
        trip = self.trips[trip_id]
        trip.complete()
        route = self.routes[trip.route_id]
        vehicle = self.vehicles[trip.vehicle_id]
        vehicle.mileage_km += route.distance_km

        has_open_service = False
        for record in vehicle.maintenance_records:
            if not record.service_completed:
                has_open_service = True
        if has_open_service:
            vehicle.update_status(VehicleStatus.MAINTENANCE)
        else:
            vehicle.update_status(VehicleStatus.AVAILABLE)
        self.drivers[trip.driver_id].availability_status = True
        return trip

    def add_maintenance_record(self, record: MaintenanceRecord):
        if record.record_id in self.maintenance_records:
            raise ValueError("Maintenance record ID already exists.")
        if record.vehicle_id not in self.vehicles:
            raise ValueError("Vehicle was not found.")
        for trip in self.trips.values():
            if trip.vehicle_id == record.vehicle_id and trip.status in (
                TripStatus.SCHEDULED, TripStatus.IN_PROGRESS
            ):
                raise ValueError("Cannot add maintenance while the vehicle has an active trip.")

        vehicle = self.vehicles[record.vehicle_id]
        vehicle.maintenance_records.append(record)
        self.maintenance_records[record.record_id] = record
        vehicle.update_status(VehicleStatus.MAINTENANCE)
        return record

    def complete_maintenance(self, record_id: str):
        if record_id not in self.maintenance_records:
            raise ValueError("Maintenance record was not found.")
        record = self.maintenance_records[record_id]
        record.complete_service()
        vehicle = self.vehicles[record.vehicle_id]

        has_open_service = False
        for other_record in vehicle.maintenance_records:
            if not other_record.service_completed:
                has_open_service = True
        if not has_open_service:
            vehicle.update_status(VehicleStatus.AVAILABLE)
        return record

    def save(self, folder=None):
        """Save each concrete class to its CSV file."""
        CSVStorage(folder).save(self)

    @classmethod
    def load(cls, folder=None):
        """Load the CSV files and rebuild the transport objects."""
        system = cls()
        CSVStorage(folder).load_into(system)
        return system
