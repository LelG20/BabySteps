"""Application service and JSON persistence for the transport system."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar
from uuid import uuid4

from .models import (
    Booking, BookingStatus, Bus, Driver, Dispatcher, Fleet, MaintenanceRecord,
    Minibus, Passenger, Payment, PaymentMethod, PaymentStatus, Route, Stop,
    Ticket, Trip, TripStatus, Vehicle, VehicleStatus,
)

T = TypeVar("T")


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Cannot serialize {type(value).__name__}")


class TransportSystem:
    """Coordinates trips, bookings, payments, fleets, and maintenance."""

    def __init__(self) -> None:
        self.passengers: dict[str, Passenger] = {}
        self.drivers: dict[str, Driver] = {}
        self.dispatchers: dict[str, Dispatcher] = {}
        self.vehicles: dict[str, Vehicle] = {}
        self.routes: dict[str, Route] = {}
        self.fleets: dict[str, Fleet] = {}
        self.trips: dict[str, Trip] = {}
        self.bookings: dict[str, Booking] = {}
        self.payments: dict[str, Payment] = {}
        self.maintenance_records: dict[str, MaintenanceRecord] = {}

    @staticmethod
    def _add(collection: dict[str, T], key: str, value: T) -> T:
        if key in collection:
            raise ValueError(f"ID {key} already exists.")
        collection[key] = value
        return value

    def add_passenger(self, passenger: Passenger) -> Passenger:
        return self._add(self.passengers, passenger.person_id, passenger)

    def add_driver(self, driver: Driver) -> Driver:
        return self._add(self.drivers, driver.person_id, driver)

    def add_dispatcher(self, dispatcher: Dispatcher) -> Dispatcher:
        return self._add(self.dispatchers, dispatcher.person_id, dispatcher)

    def add_vehicle(self, vehicle: Vehicle, fleet_id: str | None = None) -> Vehicle:
        self._add(self.vehicles, vehicle.vehicle_id, vehicle)
        if fleet_id:
            self._require(self.fleets, fleet_id, "Fleet").add_vehicle(vehicle)
        return vehicle

    def add_route(self, route: Route) -> Route:
        return self._add(self.routes, route.route_id, route)

    def add_fleet(self, fleet: Fleet) -> Fleet:
        return self._add(self.fleets, fleet.fleet_id, fleet)

    @staticmethod
    def _require(collection: dict[str, T], key: str, label: str) -> T:
        try:
            return collection[key]
        except KeyError as exc:
            raise ValueError(f"{label} {key} was not found.") from exc

    @staticmethod
    def _overlaps(start: datetime, end: datetime, other_start: datetime,
                  other_end: datetime) -> bool:
        return start < other_end and other_start < end

    def schedule_trip(self, route_id: str, vehicle_id: str, driver_id: str,
                      departure_time: datetime, arrival_time: datetime,
                      dispatcher_id: str | None = None, trip_id: str | None = None) -> Trip:
        route = self._require(self.routes, route_id, "Route")
        vehicle = self._require(self.vehicles, vehicle_id, "Vehicle")
        driver = self._require(self.drivers, driver_id, "Driver")
        if dispatcher_id:
            self._require(self.dispatchers, dispatcher_id, "Dispatcher")
        if arrival_time <= departure_time:
            raise ValueError("Trip arrival must be later than departure.")
        if vehicle.status == VehicleStatus.MAINTENANCE:
            raise ValueError("A vehicle under maintenance cannot be scheduled.")
        if not driver.is_license_valid(departure_time.date()):
            raise ValueError("The driver's license is missing or expired by departure date.")
        if not driver.availability_status:
            raise ValueError("The driver is marked unavailable.")
        for existing in self.trips.values():
            if existing.status not in (TripStatus.SCHEDULED, TripStatus.IN_PROGRESS):
                continue
            if not self._overlaps(departure_time, arrival_time,
                                  existing.departure_time, existing.arrival_time):
                continue
            if existing.vehicle_id == vehicle_id:
                raise ValueError(f"Vehicle {vehicle_id} is already assigned to an overlapping trip.")
            if existing.driver_id == driver_id:
                raise ValueError(f"Driver {driver_id} is already assigned to an overlapping trip.")
        trip = Trip(trip_id or _new_id("TRIP"), route.route_id, vehicle.vehicle_id,
                    driver.person_id, departure_time, arrival_time, dispatcher_id)
        return self._add(self.trips, trip.trip_id, trip)

    def available_seats(self, trip_id: str) -> list[int]:
        trip = self._require(self.trips, trip_id, "Trip")
        vehicle = self._require(self.vehicles, trip.vehicle_id, "Vehicle")
        occupied = {b.seat_number for b in self.bookings.values()
                    if b.trip_id == trip_id and b.status == BookingStatus.CONFIRMED}
        return [seat for seat in range(1, vehicle.seat_capacity + 1) if seat not in occupied]

    def book_trip(self, passenger_id: str, trip_id: str,
                  seat_number: int | None = None) -> Booking:
        passenger = self._require(self.passengers, passenger_id, "Passenger")
        trip = self._require(self.trips, trip_id, "Trip")
        if trip.status != TripStatus.SCHEDULED:
            raise ValueError("Bookings are only available for scheduled trips.")
        open_seats = self.available_seats(trip_id)
        if not open_seats:
            raise ValueError("This trip is fully booked.")
        if seat_number is None:
            seat_number = open_seats[0]
        elif seat_number not in open_seats:
            raise ValueError(f"Seat {seat_number} is unavailable or outside the vehicle capacity.")
        fare = self._require(self.routes, trip.route_id, "Route").calculate_fare()
        booking = Booking(_new_id("BOOK"), passenger.person_id, trip.trip_id,
                          datetime.now(), seat_number, fare,
                          ticket=Ticket(_new_id("TKT"), date.today(), uuid4().hex))
        return self._add(self.bookings, booking.booking_id, booking)

    def cancel_booking(self, booking_id: str) -> Booking:
        booking = self._require(self.bookings, booking_id, "Booking")
        if booking.status == BookingStatus.CANCELLED:
            raise ValueError("Booking is already cancelled.")
        booking.cancel()
        for payment in self.payments.values():
            if payment.booking_id == booking_id:
                payment.refund()
        return booking

    def process_payment(self, booking_id: str, method: PaymentMethod,
                        amount: float | None = None) -> Payment:
        booking = self._require(self.bookings, booking_id, "Booking")
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError("Payment cannot be made for a cancelled booking.")
        if any(p.booking_id == booking_id and p.status == PaymentStatus.PAID
               for p in self.payments.values()):
            raise ValueError("This booking has already been paid.")
        amount = booking.total_amount if amount is None else round(amount, 2)
        if amount != booking.total_amount:
            raise ValueError(f"Payment must equal the fare of {booking.total_amount:.2f}.")
        payment = Payment(_new_id("PAY"), booking_id, amount, method)
        if not payment.process_payment():
            raise ValueError("Payment failed.")
        self._add(self.payments, payment.payment_id, payment)
        self.passengers[booking.passenger_id].loyalty_points += int(amount)
        return payment

    def start_trip(self, trip_id: str) -> Trip:
        trip = self._require(self.trips, trip_id, "Trip")
        trip.start()
        self.vehicles[trip.vehicle_id].update_status(VehicleStatus.IN_SERVICE)
        self.drivers[trip.driver_id].availability_status = False
        return trip

    def complete_trip(self, trip_id: str) -> Trip:
        trip = self._require(self.trips, trip_id, "Trip")
        trip.complete()
        self.vehicles[trip.vehicle_id].mileage_km += self.routes[trip.route_id].distance_km
        self.vehicles[trip.vehicle_id].update_status(VehicleStatus.AVAILABLE)
        self.drivers[trip.driver_id].availability_status = True
        return trip

    def cancel_trip(self, trip_id: str) -> Trip:
        trip = self._require(self.trips, trip_id, "Trip")
        trip.cancel()
        for booking in self.bookings.values():
            if booking.trip_id == trip_id and booking.status == BookingStatus.CONFIRMED:
                self.cancel_booking(booking.booking_id)
        return trip

    def add_maintenance_record(self, record: MaintenanceRecord) -> MaintenanceRecord:
        vehicle = self._require(self.vehicles, record.vehicle_id, "Vehicle")
        self._add(self.maintenance_records, record.record_id, record)
        vehicle.update_status(VehicleStatus.MAINTENANCE)
        return record

    def complete_maintenance(self, record_id: str) -> MaintenanceRecord:
        record = self._require(self.maintenance_records, record_id, "Maintenance record")
        record.complete_service()
        vehicle = self.vehicles[record.vehicle_id]
        if not any(r.vehicle_id == vehicle.vehicle_id and r.next_service_date is not None
                   for r in self.maintenance_records.values()):
            vehicle.update_status(VehicleStatus.AVAILABLE)
        return record

    def save(self, path: str | Path) -> None:
        collections = ("passengers", "drivers", "dispatchers", "vehicles", "routes",
                       "fleets", "trips", "bookings", "payments", "maintenance_records")
        payload = {name: [asdict(item) for item in getattr(self, name).values()]
                   for name in collections}
        Path(path).write_text(json.dumps(payload, default=_json_default, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> TransportSystem:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        system = cls()
        def add_all(section: str, factory: Any, key: str, convert: Any = None) -> None:
            for raw in data.get(section, []):
                item = factory(raw)
                if convert:
                    item = convert(item)
                getattr(system, section)[getattr(item, key)] = item

        add_all("passengers", lambda d: Passenger(**{**d, "preferred_payment": PaymentMethod(d.get("preferred_payment", "mpesa"))}), "person_id")
        add_all("drivers", lambda d: Driver(**{**d, "license_expiry": date.fromisoformat(d["license_expiry"])}), "person_id")
        add_all("dispatchers", Dispatcher, "person_id")
        def make_vehicle(d: dict[str, Any]) -> Vehicle:
            d = dict(d)
            d["status"] = VehicleStatus(d.get("status", "available"))
            cls_name = d.pop("vehicle_type", None)
            if "has_air_conditioning" in d:
                return Bus(**d)
            if "permit_number" in d:
                return Minibus(**d)
            return Vehicle(**d)
        add_all("vehicles", make_vehicle, "vehicle_id")
        add_all("routes", lambda d: Route(**{**d, "stops": [Stop(**s) for s in d.get("stops", [])]}), "route_id")
        add_all("fleets", Fleet, "fleet_id")
        add_all("trips", lambda d: Trip(**{**d, "departure_time": datetime.fromisoformat(d["departure_time"]), "arrival_time": datetime.fromisoformat(d["arrival_time"]), "status": TripStatus(d.get("status", "scheduled"))}), "trip_id")
        add_all("bookings", lambda d: Booking(**{**d, "booking_date": datetime.fromisoformat(d["booking_date"]), "status": BookingStatus(d.get("status", "confirmed")), "ticket": Ticket(**{**d["ticket"], "issue_date": date.fromisoformat(d["ticket"]["issue_date"])}) if d.get("ticket") else None}), "booking_id")
        add_all("payments", lambda d: Payment(**{**d, "method": PaymentMethod(d["method"]), "status": PaymentStatus(d.get("status", "pending")), "paid_at": datetime.fromisoformat(d["paid_at"]) if d.get("paid_at") else None}), "payment_id")
        add_all("maintenance_records", lambda d: MaintenanceRecord(**{**d, "service_date": date.fromisoformat(d["service_date"]), "next_service_date": date.fromisoformat(d["next_service_date"]) if d.get("next_service_date") else None}), "record_id")
        return system
