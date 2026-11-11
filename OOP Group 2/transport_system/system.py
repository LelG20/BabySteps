"""Application rules and simple JSON saving for the transport system."""
import json
from dataclasses import asdict
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from uuid import uuid4

from .models import (
    Booking, BookingStatus, Bus, Driver, Dispatcher, Fleet, MaintenanceRecord,
    Minibus, Passenger, Payment, PaymentMethod, PaymentStatus, Route, Stop,
    Ticket, Trip, TripStatus, Vehicle, VehicleStatus,
)


def _new_id(prefix: str) -> str:
    return prefix + "-" + uuid4().hex[:6].upper()


def _json_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    raise TypeError("Value cannot be saved as JSON")


# ==================== PRESENTER: Maryhope ====================
# TransportSystem holds the main objects used by the program.
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


# ==================== PRESENTER: Mitch ====================
# These methods check the UML relationship counts before creating objects.
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
            overlaps = departure_time < existing.arrival_time and existing.departure_time < arrival_time
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
            if booking.trip_id == trip_id and booking.status == BookingStatus.CONFIRMED:
                occupied.append(booking.seat_number)
        seats = []
        for number in range(1, vehicle.seat_capacity + 1):
            if number not in occupied:
                seats.append(number)
        return seats


# ==================== PRESENTER: Jesse ====================
# This is the main path from a passenger request to a saved Booking object.
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
        booking_id = _new_id("BOOKING")
        booking = Booking(booking_id, passenger_id, trip_id, datetime.now(),
                          seat_number, fare, ticket=ticket)
        booking.confirm()
        self.bookings[booking_id] = booking
        return booking

    def cancel_booking(self, booking_id: str):
        booking = self.bookings[booking_id]
        booking.cancel()
        for payment in self.payments.values():
            if payment.booking_id == booking_id:
                payment.refund()
        return booking


# ==================== PRESENTER: Leon ====================
# This creates a local payment record; it does not contact a real provider.
    def process_payment(self, booking_id: str, method: PaymentMethod):
        booking = self.bookings[booking_id]
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError("A cancelled booking cannot be paid for.")
        for payment in self.payments.values():
            if payment.booking_id == booking_id and payment.status == PaymentStatus.PAID:
                raise ValueError("This booking already has a completed payment.")
        payment = Payment(_new_id("PAYMENT"), booking_id,
                          booking.total_amount, method)
        if not payment.process_payment():
            raise ValueError("Payment amount must be greater than zero.")
        self.payments[payment.payment_id] = payment
        self.passengers[booking.passenger_id].loyalty_points += int(payment.amount)
        return payment


# ==================== PRESENTER: Jackson ====================
# These functions call the Trip methods and update related objects.
    def start_trip(self, trip_id: str):
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


# Maintenance records are stored on their vehicle and in the system index.
    def add_maintenance_record(self, record: MaintenanceRecord):
        if record.record_id in self.maintenance_records:
            raise ValueError("Maintenance record ID already exists.")
        vehicle = self.vehicles[record.vehicle_id]
        for trip in self.trips.values():
            if trip.vehicle_id == record.vehicle_id and trip.status in (
                TripStatus.SCHEDULED, TripStatus.IN_PROGRESS
            ):
                raise ValueError("Cannot add maintenance while the vehicle has an active trip.")
        vehicle.maintenance_records.append(record)
        self.maintenance_records[record.record_id] = record
        vehicle.update_status(VehicleStatus.MAINTENANCE)
        return record

    def complete_maintenance(self, record_id: str):
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

    def save(self, file_path):
        """Write the current objects to a JSON file."""
        data = {}
        names = ["passengers", "drivers", "dispatchers", "vehicles", "routes",
                 "fleets", "trips", "bookings", "payments", "maintenance_records"]
        for name in names:
            data[name] = []
            for item in getattr(self, name).values():
                item_data = asdict(item)
                if name == "vehicles":
                    item_data.pop("maintenance_records", None)
                data[name].append(item_data)
        Path(file_path).write_text(
            json.dumps(data, default=_json_value, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, file_path):
        """Rebuild the stored objects from a JSON file."""
        path = Path(file_path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        system = cls()

        for row in data.get("passengers", []):
            row["preferred_payment"] = PaymentMethod(row.get("preferred_payment", "mpesa"))
            person = Passenger(**row)
            system.passengers[person.person_id] = person
        for row in data.get("drivers", []):
            row["license_expiry"] = date.fromisoformat(row["license_expiry"])
            person = Driver(**row)
            system.drivers[person.person_id] = person
        for row in data.get("dispatchers", []):
            person = Dispatcher(**row)
            system.dispatchers[person.person_id] = person
        for row in data.get("fleets", []):
            fleet = Fleet(**row)
            system.fleets[fleet.fleet_id] = fleet
        for row in data.get("routes", []):
            row["stops"] = [Stop(**stop) for stop in row.get("stops", [])]
            route = Route(**row)
            system.routes[route.route_id] = route
        for row in data.get("vehicles", []):
            row["status"] = VehicleStatus(row.get("status", "available"))
            if "has_air_conditioning" in row:
                vehicle = Bus(**row)
            else:
                vehicle = Minibus(**row)
            system.vehicles[vehicle.vehicle_id] = vehicle
        for row in data.get("trips", []):
            row["departure_time"] = datetime.fromisoformat(row["departure_time"])
            row["arrival_time"] = datetime.fromisoformat(row["arrival_time"])
            row["status"] = TripStatus(row.get("status", "scheduled"))
            trip = Trip(**row)
            system.trips[trip.trip_id] = trip
        for row in data.get("maintenance_records", []):
            row["service_date"] = date.fromisoformat(row["service_date"])
            if row.get("next_service_date"):
                row["next_service_date"] = date.fromisoformat(row["next_service_date"])
            record = MaintenanceRecord(**row)
            system.maintenance_records[record.record_id] = record
            if record.vehicle_id in system.vehicles:
                system.vehicles[record.vehicle_id].maintenance_records.append(record)
        for row in data.get("bookings", []):
            row["booking_date"] = datetime.fromisoformat(row["booking_date"])
            row["status"] = BookingStatus(row.get("status", "confirmed"))
            if row.get("ticket"):
                ticket_data = row["ticket"]
                ticket_data["issue_date"] = date.fromisoformat(ticket_data["issue_date"])
                row["ticket"] = Ticket(**ticket_data)
            booking = Booking(**row)
            system.bookings[booking.booking_id] = booking
        for row in data.get("payments", []):
            row["method"] = PaymentMethod(row["method"])
            row["status"] = PaymentStatus(row.get("status", "pending"))
            if row.get("paid_at"):
                row["paid_at"] = datetime.fromisoformat(row["paid_at"])
            payment = Payment(**row)
            system.payments[payment.payment_id] = payment
        return system
