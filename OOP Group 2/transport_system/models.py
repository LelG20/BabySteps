"""Domain entities for the Transport Management System."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from abc import ABC


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


@dataclass
class Person(ABC):
    person_id: str
    full_name: str
    phone_number: str
    email: str = ""

    def __post_init__(self) -> None:
        if not self.person_id.strip() or not self.full_name.strip():
            raise ValueError("Person ID and full name are required.")
        if not self.phone_number.strip():
            raise ValueError("Phone number is required.")

    def get_contact_details(self) -> str:
        return f"{self.full_name} | {self.phone_number} | {self.email}".rstrip(" |")

    def update_profile(self, *, full_name: str | None = None,
                       phone_number: str | None = None,
                       email: str | None = None) -> None:
        if full_name is not None and full_name.strip():
            self.full_name = full_name.strip()
        if phone_number is not None and phone_number.strip():
            self.phone_number = phone_number.strip()
        if email is not None:
            self.email = email.strip()


@dataclass
class Passenger(Person):
    loyalty_points: int = 0
    preferred_payment: PaymentMethod = PaymentMethod.MPESA


@dataclass
class Driver(Person):
    license_number: str = ""
    license_expiry: date = field(default_factory=date.today)
    availability_status: bool = True
    years_experience: int = 0

    def is_license_valid(self, on_date: date | None = None) -> bool:
        return bool(self.license_number.strip()) and self.license_expiry >= (on_date or date.today())


@dataclass
class Dispatcher(Person):
    employee_id: str = ""
    shift: str = ""

    def schedule_trip(self, trip: Trip) -> Trip:
        return trip


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
            raise ValueError("Route distance/duration must be positive and fare cannot be negative.")

    def calculate_fare(self) -> float:
        return round(self.base_fare, 2)

    def get_stops(self) -> list[Stop]:
        return list(self.stops)

    def add_stop(self, stop: Stop) -> None:
        if any(existing.stop_id == stop.stop_id for existing in self.stops):
            raise ValueError(f"Stop {stop.stop_id} is already on this route.")
        self.stops.append(stop)


@dataclass
class Vehicle(ABC):
    vehicle_id: str
    registration_number: str
    make: str
    model: str
    seat_capacity: int
    mileage_km: float = 0
    status: VehicleStatus = VehicleStatus.AVAILABLE

    def __post_init__(self) -> None:
        if not self.vehicle_id or not self.registration_number.strip():
            raise ValueError("Vehicle ID and registration number are required.")
        if self.seat_capacity <= 0 or self.mileage_km < 0:
            raise ValueError("Seat capacity must be positive and mileage cannot be negative.")

    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE

    def update_status(self, status: VehicleStatus) -> None:
        self.status = status

    def assign_to_trip(self, trip: Trip) -> None:
        if not self.is_available():
            raise ValueError(f"Vehicle {self.registration_number} is not available.")
        trip.vehicle_id = self.vehicle_id

    def get_service_history(self, records: list[MaintenanceRecord]) -> list[MaintenanceRecord]:
        return [record for record in records if record.vehicle_id == self.vehicle_id]


@dataclass
class Bus(Vehicle):
    has_air_conditioning: bool = False
    luggage_capacity_kg: float = 0

    def get_luggage_space(self) -> float:
        return self.luggage_capacity_kg


@dataclass
class Minibus(Vehicle):
    permit_number: str = ""
    is_city_route: bool = False

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

    def remove_vehicle(self, vehicle_id: str) -> None:
        if vehicle_id in self.vehicle_ids:
            self.vehicle_ids.remove(vehicle_id)

    def get_available_vehicles(self, vehicles: dict[str, Vehicle]) -> list[Vehicle]:
        return [vehicles[vid] for vid in self.vehicle_ids
                if vid in vehicles and vehicles[vid].is_available()]

    def get_fleet_size(self) -> int:
        return len(self.vehicle_ids)


@dataclass
class Trip:
    trip_id: str
    route_id: str
    vehicle_id: str
    driver_id: str
    departure_time: datetime
    arrival_time: datetime
    dispatcher_id: str | None = None
    status: TripStatus = TripStatus.SCHEDULED

    def __post_init__(self) -> None:
        if self.arrival_time <= self.departure_time:
            raise ValueError("Trip arrival must be later than departure.")

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
            raise ValueError("Completed or cancelled trips cannot be cancelled again.")
        self.status = TripStatus.CANCELLED


@dataclass
class Ticket:
    ticket_number: str
    issue_date: date
    qr_code: str

    def generate_ticket(self) -> str:
        return self.qr_code

    def validate(self) -> bool:
        return bool(self.ticket_number.strip() and self.qr_code.strip())


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

    def confirm(self) -> None:
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("A cancelled booking cannot be confirmed.")
        self.status = BookingStatus.CONFIRMED

    def cancel(self) -> None:
        self.status = BookingStatus.CANCELLED

    def calculate_total(self) -> float:
        return round(self.total_amount, 2)


@dataclass
class Payment:
    payment_id: str
    booking_id: str
    amount: float
    method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    paid_at: datetime | None = None

    def process_payment(self) -> bool:
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


@dataclass
class MaintenanceRecord:
    record_id: str
    vehicle_id: str
    service_date: date
    description: str
    cost: float
    next_service_date: date | None = None

    def __post_init__(self) -> None:
        if self.cost < 0:
            raise ValueError("Maintenance cost cannot be negative.")

    def schedule_service(self) -> None:
        if self.next_service_date is None:
            raise ValueError("Set a next service date before scheduling service.")

    def complete_service(self) -> None:
        self.next_service_date = None
