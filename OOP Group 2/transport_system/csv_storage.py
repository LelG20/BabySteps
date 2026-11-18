"""Read and write transport-system objects as separate CSV files."""
import csv
from datetime import date, datetime
from pathlib import Path

from .models import (
    Booking, BookingStatus, Bus, Dispatcher, Driver, Fleet, MaintenanceRecord,
    Minibus, Passenger, Payment, PaymentMethod, PaymentStatus, Route, Stop,
    Ticket, Trip, TripStatus, VehicleStatus,
)


# The data folder sits beside the transport_system package.
DEFAULT_DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"


class CSVStorage:
    def __init__(self, folder=None):
        self.folder = Path(folder) if folder else DEFAULT_DATA_FOLDER

    def read_rows(self, file_name):
        path = self.folder / file_name
        if not path.exists():
            return []

        with path.open("r", newline="", encoding="utf-8") as csv_file:
            return list(csv.DictReader(csv_file))

    def write_rows(self, file_name, columns, rows):
        self.folder.mkdir(parents=True, exist_ok=True)
        path = self.folder / file_name

        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def load_into(self, system):
        # Load people and fleets before loading objects that refer to them.
        for row in self.read_rows("passengers.csv"):
            passenger = Passenger(
                person_id=row["person_id"],
                full_name=row["full_name"],
                phone_number=row["phone_number"],
                email=row.get("email", ""),
                loyalty_points=int(row.get("loyalty_points", 0)),
                preferred_payment=PaymentMethod(
                    row.get("preferred_payment", "mpesa") or "mpesa"
                ),
            )
            system.add_passenger(passenger)

        for row in self.read_rows("drivers.csv"):
            driver = Driver(
                person_id=row["person_id"],
                full_name=row["full_name"],
                phone_number=row["phone_number"],
                email=row.get("email", ""),
                license_number=row["license_number"],
                license_expiry=date.fromisoformat(row["license_expiry"]),
                availability_status=self._read_bool(row["availability_status"]),
                years_experience=int(row.get("years_experience", 0)),
            )
            system.add_driver(driver)

        for row in self.read_rows("driver_issues.csv"):
            driver_id = row["driver_id"]
            if driver_id in system.drivers:
                system.drivers[driver_id].reported_issues.append(row["issue_text"])

        for row in self.read_rows("dispatchers.csv"):
            dispatcher = Dispatcher(
                person_id=row["person_id"],
                full_name=row["full_name"],
                phone_number=row["phone_number"],
                email=row.get("email", ""),
                employee_id=row["employee_id"],
                shift=row["shift"],
            )
            system.add_dispatcher(dispatcher)

        for row in self.read_rows("fleets.csv"):
            fleet = Fleet(
                fleet_id=row["fleet_id"],
                fleet_name=row["fleet_name"],
                depot_location=row["depot_location"],
            )
            system.add_fleet(fleet)

        # Stops are stored separately and linked to their route by route_id.
        stops_by_route = {}
        for row in self.read_rows("stops.csv"):
            stop = Stop(row["stop_id"], row["stop_name"], row["location"])
            stops_by_route.setdefault(row["route_id"], []).append(stop)

        for row in self.read_rows("routes.csv"):
            route_id = row["route_id"]
            route = Route(
                route_id=route_id,
                origin=row["origin"],
                destination=row["destination"],
                distance_km=float(row["distance_km"]),
                estimated_duration_min=int(row["estimated_duration_min"]),
                base_fare=float(row["base_fare"]),
                stops=stops_by_route.get(route_id, []),
            )
            system.add_route(route)

        # Bus and Minibus are concrete Vehicle classes, so each has its own file.
        for row in self.read_rows("buses.csv"):
            bus = Bus(
                vehicle_id=row["vehicle_id"],
                registration_number=row["registration_number"],
                make=row["make"],
                model=row["model"],
                seat_capacity=int(row["seat_capacity"]),
                mileage_km=float(row["mileage_km"]),
                status=VehicleStatus(row["status"]),
                has_air_conditioning=self._read_bool(row["has_air_conditioning"]),
                luggage_capacity_kg=float(row["luggage_capacity_kg"]),
            )
            system.add_vehicle(bus, row["fleet_id"])

        for row in self.read_rows("minibuses.csv"):
            minibus = Minibus(
                vehicle_id=row["vehicle_id"],
                registration_number=row["registration_number"],
                make=row["make"],
                model=row["model"],
                seat_capacity=int(row["seat_capacity"]),
                mileage_km=float(row["mileage_km"]),
                status=VehicleStatus(row["status"]),
                permit_number=row["permit_number"],
                is_city_route=self._read_bool(row["is_city_route"]),
            )
            system.add_vehicle(minibus, row["fleet_id"])

        for row in self.read_rows("trips.csv"):
            trip = Trip(
                trip_id=row["trip_id"],
                route_id=row["route_id"],
                vehicle_id=row["vehicle_id"],
                driver_id=row["driver_id"],
                departure_time=datetime.fromisoformat(row["departure_time"]),
                arrival_time=datetime.fromisoformat(row["arrival_time"]),
                dispatcher_id=row["dispatcher_id"],
                status=TripStatus(row["status"]),
            )
            self._check_trip_links(trip, system)
            system.trips[trip.trip_id] = trip

        # Each maintenance record is also kept in its vehicle's service history.
        for row in self.read_rows("maintenance_records.csv"):
            next_date = row.get("next_service_date", "")
            record = MaintenanceRecord(
                record_id=row["record_id"],
                vehicle_id=row["vehicle_id"],
                service_date=date.fromisoformat(row["service_date"]),
                description=row["description"],
                cost=float(row["cost"]),
                next_service_date=date.fromisoformat(next_date) if next_date else None,
                service_completed=self._read_bool(row.get("service_completed", "false")),
            )
            if record.vehicle_id not in system.vehicles:
                raise ValueError("Maintenance record refers to a missing vehicle.")
            system.maintenance_records[record.record_id] = record
            system.vehicles[record.vehicle_id].maintenance_records.append(record)

        tickets_by_booking = {}
        for row in self.read_rows("tickets.csv"):
            tickets_by_booking[row["booking_id"]] = Ticket(
                ticket_number=row["ticket_number"],
                issue_date=date.fromisoformat(row["issue_date"]),
                qr_code=row["qr_code"],
            )

        for row in self.read_rows("bookings.csv"):
            booking = Booking(
                booking_id=row["booking_id"],
                passenger_id=row["passenger_id"],
                trip_id=row["trip_id"],
                booking_date=datetime.fromisoformat(row["booking_date"]),
                seat_number=int(row["seat_number"]),
                total_amount=float(row["total_amount"]),
                status=BookingStatus(row["status"]),
                ticket=tickets_by_booking.get(row["booking_id"]),
            )
            if booking.passenger_id not in system.passengers:
                raise ValueError("Booking refers to a missing passenger.")
            if booking.trip_id not in system.trips:
                raise ValueError("Booking refers to a missing trip.")
            system.bookings[booking.booking_id] = booking

        for row in self.read_rows("payments.csv"):
            paid_at = row.get("paid_at", "")
            payment = Payment(
                payment_id=row["payment_id"],
                booking_id=row["booking_id"],
                amount=float(row["amount"]),
                method=PaymentMethod(row["method"]),
                status=PaymentStatus(row["status"]),
                paid_at=datetime.fromisoformat(paid_at) if paid_at else None,
            )
            if payment.booking_id not in system.bookings:
                raise ValueError("Payment refers to a missing booking.")
            system.payments[payment.payment_id] = payment

    def save(self, system):
        # Write people and fleet records.
        self.write_rows("passengers.csv", [
            "person_id", "full_name", "phone_number", "email",
            "loyalty_points", "preferred_payment",
        ], [
            {
                "person_id": p.person_id,
                "full_name": p.full_name,
                "phone_number": p.phone_number,
                "email": p.email,
                "loyalty_points": p.loyalty_points,
                "preferred_payment": p.preferred_payment.value,
            }
            for p in system.passengers.values()
        ])

        self.write_rows("drivers.csv", [
            "person_id", "full_name", "phone_number", "email", "license_number",
            "license_expiry", "availability_status", "years_experience",
        ], [
            {
                "person_id": d.person_id,
                "full_name": d.full_name,
                "phone_number": d.phone_number,
                "email": d.email,
                "license_number": d.license_number,
                "license_expiry": d.license_expiry.isoformat(),
                "availability_status": str(d.availability_status).lower(),
                "years_experience": d.years_experience,
            }
            for d in system.drivers.values()
        ])
        issue_rows = []
        for driver in system.drivers.values():
            for issue in driver.reported_issues:
                issue_rows.append({"driver_id": driver.person_id, "issue_text": issue})
        self.write_rows("driver_issues.csv", ["driver_id", "issue_text"], issue_rows)

        self.write_rows("dispatchers.csv", [
            "person_id", "full_name", "phone_number", "email", "employee_id", "shift",
        ], [
            {
                "person_id": d.person_id,
                "full_name": d.full_name,
                "phone_number": d.phone_number,
                "email": d.email,
                "employee_id": d.employee_id,
                "shift": d.shift,
            }
            for d in system.dispatchers.values()
        ])
        self.write_rows("fleets.csv", [
            "fleet_id", "fleet_name", "depot_location",
        ], [
            {
                "fleet_id": f.fleet_id,
                "fleet_name": f.fleet_name,
                "depot_location": f.depot_location,
            }
            for f in system.fleets.values()
        ])

        # Save each vehicle type in its own file and keep its fleet ID as a link.
        fleet_for_vehicle = {}
        for fleet in system.fleets.values():
            for vehicle_id in fleet.vehicle_ids:
                fleet_for_vehicle[vehicle_id] = fleet.fleet_id

        bus_rows = []
        minibus_rows = []
        for vehicle in system.vehicles.values():
            if vehicle.vehicle_id not in fleet_for_vehicle:
                raise ValueError("Every vehicle must belong to one fleet before saving.")
            common = {
                "vehicle_id": vehicle.vehicle_id,
                "registration_number": vehicle.registration_number,
                "make": vehicle.make,
                "model": vehicle.model,
                "seat_capacity": vehicle.seat_capacity,
                "mileage_km": vehicle.mileage_km,
                "status": vehicle.status.value,
                "fleet_id": fleet_for_vehicle[vehicle.vehicle_id],
            }
            if isinstance(vehicle, Bus):
                bus_rows.append({
                    **common,
                    "has_air_conditioning": str(vehicle.has_air_conditioning).lower(),
                    "luggage_capacity_kg": vehicle.luggage_capacity_kg,
                })
            elif isinstance(vehicle, Minibus):
                minibus_rows.append({
                    **common,
                    "permit_number": vehicle.permit_number,
                    "is_city_route": str(vehicle.is_city_route).lower(),
                })

        self.write_rows("buses.csv", [
            "vehicle_id", "registration_number", "make", "model", "seat_capacity",
            "mileage_km", "status", "has_air_conditioning", "luggage_capacity_kg", "fleet_id",
        ], bus_rows)
        self.write_rows("minibuses.csv", [
            "vehicle_id", "registration_number", "make", "model", "seat_capacity",
            "mileage_km", "status", "permit_number", "is_city_route", "fleet_id",
        ], minibus_rows)

        # Save routes and their stops in separate files, joined by route_id.
        route_rows = []
        stop_rows = []
        for route in system.routes.values():
            route_rows.append({
                "route_id": route.route_id,
                "origin": route.origin,
                "destination": route.destination,
                "distance_km": route.distance_km,
                "estimated_duration_min": route.estimated_duration_min,
                "base_fare": route.base_fare,
            })
            for stop in route.stops:
                stop_rows.append({
                    "stop_id": stop.stop_id,
                    "route_id": route.route_id,
                    "stop_name": stop.stop_name,
                    "location": stop.location,
                })
        self.write_rows("routes.csv", [
            "route_id", "origin", "destination", "distance_km",
            "estimated_duration_min", "base_fare",
        ], route_rows)
        self.write_rows("stops.csv", ["stop_id", "route_id", "stop_name", "location"], stop_rows)

        self.write_rows("trips.csv", [
            "trip_id", "route_id", "vehicle_id", "driver_id", "departure_time",
            "arrival_time", "dispatcher_id", "status",
        ], [
            {
                "trip_id": t.trip_id,
                "route_id": t.route_id,
                "vehicle_id": t.vehicle_id,
                "driver_id": t.driver_id,
                "departure_time": t.departure_time.isoformat(),
                "arrival_time": t.arrival_time.isoformat(),
                "dispatcher_id": t.dispatcher_id,
                "status": t.status.value,
            }
            for t in system.trips.values()
        ])

        # Save maintenance records from the history owned by each vehicle.
        maintenance_rows = []
        for vehicle in system.vehicles.values():
            for record in vehicle.maintenance_records:
                maintenance_rows.append({
                    "record_id": record.record_id,
                    "vehicle_id": record.vehicle_id,
                    "service_date": record.service_date.isoformat(),
                    "description": record.description,
                    "cost": record.cost,
                    "next_service_date": record.next_service_date.isoformat()
                    if record.next_service_date else "",
                    "service_completed": str(record.service_completed).lower(),
                })
        self.write_rows("maintenance_records.csv", [
            "record_id", "vehicle_id", "service_date", "description", "cost",
            "next_service_date", "service_completed",
        ], maintenance_rows)

        # A booking may own one ticket, so tickets use booking_id as their link.
        ticket_rows = []
        for booking in system.bookings.values():
            if booking.ticket is not None:
                ticket_rows.append({
                    "booking_id": booking.booking_id,
                    "ticket_number": booking.ticket.ticket_number,
                    "issue_date": booking.ticket.issue_date.isoformat(),
                    "qr_code": booking.ticket.qr_code,
                })
        self.write_rows("tickets.csv", [
            "booking_id", "ticket_number", "issue_date", "qr_code",
        ], ticket_rows)

        self.write_rows("bookings.csv", [
            "booking_id", "passenger_id", "trip_id", "booking_date", "seat_number",
            "total_amount", "status",
        ], [
            {
                "booking_id": b.booking_id,
                "passenger_id": b.passenger_id,
                "trip_id": b.trip_id,
                "booking_date": b.booking_date.isoformat(),
                "seat_number": b.seat_number,
                "total_amount": b.total_amount,
                "status": b.status.value,
            }
            for b in system.bookings.values()
        ])

        self.write_rows("payments.csv", [
            "payment_id", "booking_id", "amount", "method", "status", "paid_at",
        ], [
            {
                "payment_id": p.payment_id,
                "booking_id": p.booking_id,
                "amount": p.amount,
                "method": p.method.value,
                "status": p.status.value,
                "paid_at": p.paid_at.isoformat() if p.paid_at else "",
            }
            for p in system.payments.values()
        ])

    @staticmethod
    def _read_bool(value):
        return str(value).strip().lower() in ("true", "1", "yes", "y")

    @staticmethod
    def _check_trip_links(trip, system):
        if trip.route_id not in system.routes:
            raise ValueError("Trip refers to a missing route.")
        if trip.vehicle_id not in system.vehicles:
            raise ValueError("Trip refers to a missing vehicle.")
        if trip.driver_id not in system.drivers:
            raise ValueError("Trip refers to a missing driver.")
        if trip.dispatcher_id not in system.dispatchers:
            raise ValueError("Trip refers to a missing dispatcher.")
