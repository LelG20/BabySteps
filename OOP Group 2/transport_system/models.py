"""Transport-system objects and the data they store."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from uuid import uuid4


class TripStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    IN_SERVICE = "in_service"
    MAINTENANCE = "maintenance"


class PaymentMethod(str, Enum):
    MPESA = "mpesa"
    CARD = "card"
    CASH = "cash"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


# ==================== PRESENTER: Gyabi ====================
# Person is the shared parent class for the three kinds of people in the system.
@dataclass
class Person(ABC):
    person_id: str
    full_name: str
    phone_number: str
    email: str = ""

    def get_contact_details(self) -> str:
        return f"{self.full_name} | {self.phone_number} | {self.email}"

    def update_profile(self, full_name: str | None = None,
                       phone_number: str | None = None,
                       email: str | None = None) -> None:
        if full_name is not None:
            self.full_name = full_name
        if phone_number is not None:
            self.phone_number = phone_number
        if email is not None:
            self.email = email

    @abstractmethod
    def get_role(self) -> str:
        """Each kind of person returns its role."""
        raise NotImplementedError


@dataclass
class Passenger(Person):
    loyalty_points: int = 0
    preferred_payment: PaymentMethod = PaymentMethod.MPESA

    def get_role(self) -> str:
        return "Passenger"

    def make_booking(self, trip: Trip, system: TransportSystem,
                     seat_number: int | None = None) -> Booking:
        """Ask the system service to reserve a seat for this passenger."""
        return system.book_trip(self.person_id, trip.trip_id, seat_number)

    def cancel_booking(self, booking_id: str, system: TransportSystem) -> Booking:
        booking = system.bookings.get(booking_id)
        if booking is None or booking.passenger_id != self.person_id:
            raise ValueError("Booking does not belong to this passenger.")
        return system.cancel_booking(booking_id)

    def view_ticket(self, system: TransportSystem,
                    booking_id: str | None = None) -> Ticket:
        """Return a ticket for this passenger's selected or most recent booking."""
        passenger_bookings = []
        for booking in system.bookings.values():
            if booking.passenger_id == self.person_id:
                if booking_id is None or booking.booking_id == booking_id:
                    passenger_bookings.append(booking)
        if not passenger_bookings:
            raise ValueError("No booking was found for this passenger.")
        booking = passenger_bookings[-1]
        if booking.ticket is None:
            raise ValueError("This booking does not have a ticket.")
        return booking.ticket


@dataclass
class Driver(Person):
    license_number: str = ""
    license_expiry: date = field(default_factory=date.today)
    availability_status: bool = True
    years_experience: int = 0
    reported_issues: list[str] = field(default_factory=list)

    def get_role(self) -> str:
        return "Driver"

    def is_license_valid(self, on_date: date | None = None) -> bool:
        check_date = on_date or date.today()
        return bool(self.license_number.strip()) and self.license_expiry >= check_date

    def start_trip(self, trip: Trip, system: TransportSystem) -> Trip:
        if trip.driver_id != self.person_id:
            raise ValueError("This driver is not assigned to the trip.")
        return system.start_trip(trip.trip_id)

    def end_trip(self, trip: Trip, system: TransportSystem) -> Trip:
        if trip.driver_id != self.person_id:
            raise ValueError("This driver is not assigned to the trip.")
        return system.complete_trip(trip.trip_id)

    def report_issue(self, text: str) -> None:
        if not text.strip():
            raise ValueError("Issue text cannot be empty.")
        self.reported_issues.append(text)


@dataclass
class Dispatcher(Person):
    employee_id: str = ""
    shift: str = ""

    def get_role(self) -> str:
        return "Dispatcher"

    def schedule_trip(self, system: TransportSystem, route_id: str,
                      vehicle_id: str, driver_id: str,
                      departure_time: datetime, arrival_time: datetime,
                      trip_id: str | None = None) -> Trip:
        return system.schedule_trip(route_id, vehicle_id, driver_id,
                                    departure_time, arrival_time,
                                    self.person_id, trip_id)

    def assign_driver(self, trip: Trip, driver: Driver) -> None:
        if trip.dispatcher_id != self.person_id:
            raise ValueError("This dispatcher is not assigned to the trip.")
        if trip.status != TripStatus.SCHEDULED:
            raise ValueError("A driver can only be assigned before a trip starts.")
        if not driver.availability_status or not driver.is_license_valid(trip.departure_time.date()):
            raise ValueError("Driver is not available or has an expired license.")
        trip.driver_id = driver.person_id

    def assign_vehicle(self, trip: Trip, vehicle: Vehicle) -> None:
        if trip.dispatcher_id != self.person_id:
            raise ValueError("This dispatcher is not assigned to the trip.")
        if trip.status != TripStatus.SCHEDULED:
            raise ValueError("A vehicle can only be assigned before a trip starts.")
        vehicle.assign_to_trip(trip)

    def generate_report(self, system: TransportSystem) -> str:
        trips = []
        for trip in system.trips.values():
            if trip.dispatcher_id == self.person_id:
                trips.append(trip)
        lines = [f"Dispatcher: {self.full_name}", f"Trips managed: {len(trips)}"]
        for trip in trips:
            lines.append(f"{trip.trip_id}: {trip.status.value}")
        return "\n".join(lines)


@dataclass
class Stop:
    stop_id: str
    stop_name: str
    location: str

    def get_location(self) -> str:
        return self.location


@dataclass
class Route:
    route_id: str
    origin: str
    destination: str
    distance_km: float
    estimated_duration_min: int
    base_fare: float
    stops: list[Stop] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.route_id or not self.origin.strip() or not self.destination.strip():
            raise ValueError("Route ID, origin, and destination are required.")
        if self.distance_km <= 0 or self.estimated_duration_min <= 0 or self.base_fare < 0:
            raise ValueError("Route distance and duration must be positive; fare cannot be negative.")
        if len(self.stops) < 2:
            raise ValueError("A route must have at least two stops.")

    def calculate_fare(self) -> float:
        return round(self.base_fare, 2)

    def get_stops(self) -> list[Stop]:
        return list(self.stops)

    def add_stop(self, stop: Stop) -> None:
        self.stops.append(stop)


@dataclass
class MaintenanceRecord:
    record_id: str
    vehicle_id: str
    service_date: date
    description: str
    cost: float
    next_service_date: date | None = None
    service_completed: bool = False

    def schedule_service(self, next_service_date: date | None = None) -> None:
        if next_service_date is not None:
            self.next_service_date = next_service_date
        if self.next_service_date is None:
            raise ValueError("Set a next service date before scheduling service.")
        if self.next_service_date <= self.service_date:
            raise ValueError("Next service date must be after the current service date.")
        self.service_completed = False

    def complete_service(self) -> None:
        self.service_completed = True


# ==================== PRESENTER: Aaron ====================
# Vehicle is shared by Bus and Minibus. Its service history belongs to the vehicle.
@dataclass
class Vehicle(ABC):
    vehicle_id: str
    registration_number: str
    make: str
    model: str
    seat_capacity: int
    mileage_km: float = 0
    status: VehicleStatus = VehicleStatus.AVAILABLE
    maintenance_records: list[MaintenanceRecord] = field(default_factory=list, repr=False, kw_only=True)

    def __post_init__(self) -> None:
        if not self.vehicle_id or not self.registration_number.strip():
            raise ValueError("Vehicle ID and registration number are required.")
        if self.seat_capacity <= 0 or self.mileage_km < 0:
            raise ValueError("Vehicle must have seats and mileage cannot be negative.")

    @abstractmethod
    def get_vehicle_type(self) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE

    def update_status(self, status: VehicleStatus) -> None:
        self.status = status

    def assign_to_trip(self, trip: Trip) -> None:
        if not self.is_available():
            raise ValueError("Vehicle is not available for assignment.")
        if trip.status != TripStatus.SCHEDULED:
            raise ValueError("A vehicle can only be assigned to a scheduled trip.")
        trip.vehicle_id = self.vehicle_id

    def get_service_history(self) -> list[MaintenanceRecord]:
        return list(self.maintenance_records)


@dataclass
class Bus(Vehicle):
    has_air_conditioning: bool = False
    luggage_capacity_kg: float = 0

    def get_vehicle_type(self) -> str:
        return "Bus"

    def get_luggage_space(self) -> float:
        return self.luggage_capacity_kg


@dataclass
class Minibus(Vehicle):
    permit_number: str = ""
    is_city_route: bool = False

    def get_vehicle_type(self) -> str:
        return "Minibus"

    def is_permit_valid(self) -> bool:
        return bool(self.permit_number.strip())


@dataclass
class Fleet:
    fleet_id: str
    fleet_name: str
    depot_location: str
    vehicle_ids: list[str] = field(default_factory=list)

    def add_vehicle(self, vehicle: Vehicle) -> None:
        if vehicle.vehicle_id not in self.vehicle_ids:
            self.vehicle_ids.append(vehicle.vehicle_id)

    def remove_vehicle(self, vehicle: Vehicle | str) -> None:
        vehicle_id = vehicle.vehicle_id if isinstance(vehicle, Vehicle) else vehicle
        if vehicle_id in self.vehicle_ids:
            self.vehicle_ids.remove(vehicle_id)

    def get_available_vehicles(self, vehicles) -> list[Vehicle]:
        if hasattr(vehicles, "vehicles"):
            vehicles = vehicles.vehicles
        available = []
        for vehicle_id in self.vehicle_ids:
            if vehicle_id in vehicles and vehicles[vehicle_id].is_available():
                available.append(vehicles[vehicle_id])
        return available

    def get_fleet_size(self) -> int:
        return len(self.vehicle_ids)


# ==================== PRESENTER: Jackson ====================
# Trip stores its current state and methods move it through its simple lifecycle.
@dataclass
class Trip:
    trip_id: str
    route_id: str
    vehicle_id: str
    driver_id: str
    departure_time: datetime
    arrival_time: datetime
    dispatcher_id: str
    status: TripStatus = TripStatus.SCHEDULED

    def __post_init__(self) -> None:
        if self.arrival_time <= self.departure_time:
            raise ValueError("Trip arrival must be later than departure.")
        if not self.dispatcher_id:
            raise ValueError("A trip must have one dispatcher.")

    def start(self) -> None:
        if self.status != TripStatus.SCHEDULED:
            raise ValueError("Only a scheduled trip can start.")
        self.status = TripStatus.IN_PROGRESS

    def complete(self) -> None:
        if self.status != TripStatus.IN_PROGRESS:
            raise ValueError("Only an in-progress trip can be completed.")
        self.status = TripStatus.COMPLETED

    def cancel(self) -> None:
        if self.status in (TripStatus.COMPLETED, TripStatus.CANCELLED):
            raise ValueError("This trip cannot be cancelled.")
        self.status = TripStatus.CANCELLED

    def has_available_seat(self, system: TransportSystem) -> bool:
        return bool(system.available_seats(self.trip_id))


@dataclass
class Ticket:
    ticket_number: str = ""
    issue_date: date = field(default_factory=date.today)
    qr_code: str = ""

    def generate_ticket(self) -> None:
        if not self.ticket_number:
            self.ticket_number = "TICKET-" + uuid4().hex[:8].upper()
        if not self.qr_code:
            self.qr_code = "QR-" + uuid4().hex[:12].upper()
        self.issue_date = date.today()

    def validate(self) -> bool:
        return bool(self.ticket_number.strip() and self.qr_code.strip()
                    and self.issue_date <= date.today())


@dataclass
class Booking:
    booking_id: str
    passenger_id: str
    trip_id: str
    booking_date: datetime
    seat_number: int
    total_amount: float
    status: BookingStatus = BookingStatus.CONFIRMED
    ticket: Ticket | None = None

    def __post_init__(self) -> None:
        if self.seat_number <= 0 or self.total_amount < 0:
            raise ValueError("Seat number must be positive and fare cannot be negative.")

    def confirm(self) -> None:
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("A cancelled booking cannot be confirmed.")
        self.status = BookingStatus.CONFIRMED

    def cancel(self) -> None:
        self.status = BookingStatus.CANCELLED

    def calculate_total(self) -> float:
        return round(self.total_amount, 2)


# ==================== PRESENTER: Leon ====================
# Payments update a local status. No bank or mobile-money service is contacted.
@dataclass
class Payment:
    payment_id: str
    booking_id: str
    amount: float
    method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    paid_at: datetime | None = None

    def process_payment(self) -> bool:
        if self.status != PaymentStatus.PENDING:
            return False
        if self.amount <= 0:
            self.status = PaymentStatus.FAILED
            return False
        self.status = PaymentStatus.PAID
        self.paid_at = datetime.now()
        return True

    def refund(self) -> bool:
        if self.status != PaymentStatus.PAID:
            return False
        self.status = PaymentStatus.REFUNDED
        return True
