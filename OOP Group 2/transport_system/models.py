"""Transport-system objects and the data they store."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


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


@dataclass
class Driver(Person):
    license_number: str = ""
    license_expiry: date = field(default_factory=date.today)
    availability_status: bool = True
    years_experience: int = 0

    def get_role(self) -> str:
        return "Driver"

    def is_license_valid(self, on_date: date | None = None) -> bool:
        check_date = on_date or date.today()
        return bool(self.license_number.strip()) and self.license_expiry >= check_date


@dataclass
class Dispatcher(Person):
    employee_id: str = ""
    shift: str = ""

    def get_role(self) -> str:
        return "Dispatcher"


@dataclass
class Stop:
    stop_id: str
    stop_name: str
    location: str


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
        if len(self.stops) < 2:
            raise ValueError("A route must have at least two stops.")

    def calculate_fare(self) -> float:
        return round(self.base_fare, 2)


@dataclass
class MaintenanceRecord:
    record_id: str
    vehicle_id: str
    service_date: date
    description: str
    cost: float
    next_service_date: date | None = None

    def complete_service(self) -> None:
        self.next_service_date = None


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

    @abstractmethod
    def get_vehicle_type(self) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE

    def update_status(self, status: VehicleStatus) -> None:
        self.status = status

    def get_service_history(self) -> list[MaintenanceRecord]:
        return list(self.maintenance_records)


@dataclass
class Bus(Vehicle):
    has_air_conditioning: bool = False
    luggage_capacity_kg: float = 0

    def get_vehicle_type(self) -> str:
        return "Bus"


@dataclass
class Minibus(Vehicle):
    permit_number: str = ""
    is_city_route: bool = False

    def get_vehicle_type(self) -> str:
        return "Minibus"


@dataclass
class Fleet:
    fleet_id: str
    fleet_name: str
    depot_location: str
    vehicle_ids: list[str] = field(default_factory=list)

    def add_vehicle(self, vehicle: Vehicle) -> None:
        if vehicle.vehicle_id not in self.vehicle_ids:
            self.vehicle_ids.append(vehicle.vehicle_id)

    def get_available_vehicles(self, vehicles: dict[str, Vehicle]) -> list[Vehicle]:
        available = []
        for vehicle_id in self.vehicle_ids:
            if vehicle_id in vehicles and vehicles[vehicle_id].is_available():
                available.append(vehicles[vehicle_id])
        return available


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


@dataclass
class Ticket:
    ticket_number: str
    issue_date: date
    qr_code: str


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

    def cancel(self) -> None:
        self.status = BookingStatus.CANCELLED


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
