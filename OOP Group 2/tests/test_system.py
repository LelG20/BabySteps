import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

from transport_system import (
    BookingStatus, Bus, Dispatcher, Driver, Fleet, MaintenanceRecord, Minibus,
    Passenger, PaymentMethod, PaymentStatus, Route, Stop, TransportSystem,
    TripStatus,
)
from transport_system.models import Person, Vehicle


class TransportSystemTests(unittest.TestCase):
    def setUp(self):
        self.system = TransportSystem()
        self.system.add_passenger(Passenger("P1", "Amina Njeri", "+254700000001"))
        self.system.add_passenger(Passenger("P2", "Brian Otieno", "+254700000002"))
        self.system.add_driver(Driver("D1", "J. Kamau", "+254700000003",
                                      license_number="DL-1",
                                      license_expiry=date.today() + timedelta(days=365),
                                      years_experience=5))
        self.system.add_dispatcher(Dispatcher("DP1", "Grace Achieng", "+254700000004",
                                               employee_id="E1", shift="Day"))
        self.system.add_fleet(Fleet("F1", "Nairobi Fleet", "Nairobi Depot"))
        self.system.add_vehicle(Bus("V1", "KDA 123A", "Isuzu", "NQR", 2,
                                     has_air_conditioning=True, luggage_capacity_kg=500), "F1")
        stops = [Stop("S1", "Nairobi Terminal", "Nairobi"),
                 Stop("S2", "Nakuru Terminal", "Nakuru")]
        self.system.add_route(Route("R1", "Nairobi", "Nakuru", 160, 150, 850.0, stops))
        start = datetime.now().replace(second=0, microsecond=0) + timedelta(days=2)
        self.trip = self.system.schedule_trip("R1", "V1", "D1", start,
                                              start + timedelta(hours=3), "DP1", trip_id="T1")

    def test_booking_assigns_distinct_seats_and_cancel_releases_seat(self):
        first = self.system.book_trip("P1", "T1")
        second = self.system.book_trip("P2", "T1")
        self.assertEqual((first.seat_number, second.seat_number), (1, 2))
        self.assertEqual(self.system.available_seats("T1"), [])
        self.system.cancel_booking(first.booking_id)
        replacement = self.system.book_trip("P1", "T1", seat_number=1)
        self.assertEqual(replacement.seat_number, 1)

    def test_abstract_base_classes_and_concrete_roles(self):
        with self.assertRaises(TypeError):
            Person("X", "Test Person", "+254700000000")
        with self.assertRaises(TypeError):
            Vehicle("X", "KXX 000X", "Make", "Model", 10)

        self.assertEqual(self.system.passengers["P1"].get_role(), "Passenger")
        self.assertEqual(self.system.drivers["D1"].get_role(), "Driver")
        self.assertEqual(self.system.vehicles["V1"].get_vehicle_type(), "Bus")

    def test_person_and_passenger_uml_methods(self):
        passenger = self.system.passengers["P1"]
        self.assertIn("Amina Njeri", passenger.get_contact_details())
        passenger.update_profile(email="amina@example.test")
        self.assertEqual(passenger.email, "amina@example.test")

        booking = passenger.make_booking(self.trip, self.system)
        self.assertEqual(booking.calculate_total(), 850.0)
        self.assertTrue(self.trip.has_available_seat(self.system))
        ticket = passenger.view_ticket(self.system, booking.booking_id)
        self.assertTrue(ticket.validate())
        self.assertEqual(ticket, booking.ticket)
        passenger.cancel_booking(booking.booking_id, self.system)
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

    def test_dispatcher_and_driver_uml_methods(self):
        dispatcher = self.system.dispatchers["DP1"]
        driver = self.system.drivers["D1"]
        driver.report_issue("Check the rear light")
        self.assertEqual(driver.reported_issues, ["Check the rear light"])
        self.assertTrue(driver.is_license_valid())

        self.assertIs(driver.start_trip(self.trip, self.system), self.trip)
        self.assertIs(driver.end_trip(self.trip, self.system), self.trip)

        self.system.add_driver(Driver(
            "D2", "M. Wanjiku", "+254700000005", license_number="DL-2",
            license_expiry=date.today() + timedelta(days=365),
        ))
        self.system.add_fleet(Fleet("F2", "Second Fleet", "Nakuru Depot"))
        second_bus = Bus("V2", "KDA 456B", "Toyota", "Coaster", 14)
        self.system.add_vehicle(second_bus, "F2")
        start = self.trip.departure_time + timedelta(days=5)
        second_trip = dispatcher.schedule_trip(
            self.system, "R1", "V2", "D2", start,
            start + timedelta(hours=2), "T2",
        )
        dispatcher.assign_driver(second_trip, driver)
        dispatcher.assign_vehicle(second_trip, self.system.vehicles["V1"])
        self.assertEqual(second_trip.driver_id, "D1")
        self.assertEqual(second_trip.vehicle_id, "V1")
        self.assertIn("Trips managed: 2", dispatcher.generate_report(self.system))

    def test_route_stop_fleet_vehicle_and_vehicle_type_uml_methods(self):
        route = self.system.routes["R1"]
        self.assertEqual(route.calculate_fare(), 850.0)
        self.assertEqual(len(route.get_stops()), 2)
        route.add_stop(Stop("S3", "Central Stop", "Central"))
        self.assertEqual(route.get_stops()[-1].get_location(), "Central")

        fleet = self.system.fleets["F1"]
        self.assertEqual(fleet.get_fleet_size(), 1)
        self.assertEqual(fleet.get_available_vehicles(self.system),
                         [self.system.vehicles["V1"]])
        fleet.remove_vehicle(self.system.vehicles["V1"])
        self.assertEqual(fleet.get_fleet_size(), 0)
        fleet.add_vehicle(self.system.vehicles["V1"])

        self.assertEqual(self.system.vehicles["V1"].get_luggage_space(), 500)
        minibus = Minibus("M1", "KDA 789C", "Nissan", "Urvan", 14,
                          permit_number="PSV-1")
        self.assertTrue(minibus.is_permit_valid())
        self.assertFalse(Minibus("M2", "KDA 789D", "Nissan", "Urvan", 14)
                         .is_permit_valid())

    def test_maintenance_record_uml_methods(self):
        next_date = date.today() + timedelta(days=180)
        record = MaintenanceRecord("M1", "V1", date.today(), "Oil change", 5000,
                                   next_service_date=next_date)
        record.schedule_service()
        self.assertEqual(record.next_service_date, next_date)
        record.complete_service()
        self.assertTrue(record.service_completed)

    def test_registration_rejects_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, "Passenger ID already exists"):
            self.system.add_passenger(Passenger("P1", "Duplicate", "+254700000099"))
        with self.assertRaisesRegex(ValueError, "Fleet ID already exists"):
            self.system.add_fleet(Fleet("F1", "Duplicate", "Depot"))

    def test_vehicle_owns_maintenance_history_and_it_survives_save_load(self):
        record = MaintenanceRecord(
            "M1", "V1", date.today(), "Oil change", 8500.0,
            date.today() + timedelta(days=180),
        )
        with self.assertRaisesRegex(ValueError, "active trip"):
            self.system.add_maintenance_record(record)
        self.system.start_trip("T1")
        self.system.complete_trip("T1")
        self.system.add_maintenance_record(record)
        vehicle = self.system.vehicles["V1"]
        self.assertEqual(vehicle.status.value, "maintenance")
        self.assertEqual(vehicle.get_service_history(), [record])
        self.system.complete_maintenance("M1")
        self.assertTrue(record.service_completed)
        self.assertEqual(record.next_service_date, date.today() + timedelta(days=180))
        self.assertEqual(vehicle.status.value, "available")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transport.json"
            self.system.save(path)
            restored = TransportSystem.load(path)

        restored_vehicle = restored.vehicles["V1"]
        self.assertEqual(len(restored_vehicle.get_service_history()), 1)
        self.assertEqual(restored_vehicle.get_service_history()[0].record_id, "M1")
        self.assertIs(restored_vehicle.get_service_history()[0], restored.maintenance_records["M1"])

    def test_route_requires_two_stops_and_trip_requires_dispatcher(self):
        with self.assertRaisesRegex(ValueError, "at least two stops"):
            Route("R2", "Nairobi", "Nakuru", 160, 150, 850.0)
        with self.assertRaisesRegex(ValueError, "Dispatcher"):
            self.system.schedule_trip(
                "R1", "V1", "D1", self.trip.departure_time + timedelta(days=1),
                self.trip.arrival_time + timedelta(days=1), "MISSING",
            )

    def test_vehicle_cannot_belong_to_two_fleets(self):
        self.system.add_fleet(Fleet("F2", "Other Fleet", "Westlands Depot"))
        with self.assertRaisesRegex(ValueError, "already belongs to a fleet"):
            self.system.add_vehicle(self.system.vehicles["V1"], "F2")

    def test_prevents_overbooking_and_duplicate_seat(self):
        self.system.book_trip("P1", "T1", seat_number=1)
        with self.assertRaises(ValueError):
            self.system.book_trip("P2", "T1", seat_number=1)
        self.system.book_trip("P2", "T1", seat_number=2)
        with self.assertRaises(ValueError):
            # no third passenger is needed to check a full vehicle
            self.system.book_trip("P1", "T1")

    def test_payment_and_cancellation_refund(self):
        booking = self.system.book_trip("P1", "T1")
        payment = self.system.process_payment(booking.booking_id, PaymentMethod.MPESA)
        self.assertEqual(payment.status, PaymentStatus.PAID)
        self.assertEqual(self.system.passengers["P1"].loyalty_points, 850)
        with self.assertRaisesRegex(ValueError, "already has a completed payment"):
            self.system.process_payment(booking.booking_id, PaymentMethod.CARD)
        self.assertEqual(self.system.passengers["P1"].loyalty_points, 850)
        self.system.cancel_booking(booking.booking_id)
        self.assertEqual(payment.status, PaymentStatus.REFUNDED)
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

    def test_rejects_expired_driver_license(self):
        self.system.drivers["D1"].license_expiry = date.today() - timedelta(days=1)
        departure = datetime.now() + timedelta(days=3)
        with self.assertRaisesRegex(ValueError, "license"):
            self.system.schedule_trip("R1", "V1", "D1", departure,
                                      departure + timedelta(hours=2), "DP1")

    def test_rejects_overlapping_assignment(self):
        start = self.trip.departure_time + timedelta(minutes=30)
        with self.assertRaisesRegex(ValueError, "overlapping"):
            self.system.schedule_trip("R1", "V1", "D1", start,
                                      start + timedelta(hours=1), "DP1")

    def test_rejects_duplicate_trip_id_and_unavailable_resources(self):
        with self.assertRaisesRegex(ValueError, "Trip ID already exists"):
            self.system.schedule_trip(
                "R1", "V1", "D1", self.trip.departure_time + timedelta(days=2),
                self.trip.arrival_time + timedelta(days=2), "DP1", trip_id="T1",
            )
        self.system.drivers["D1"].availability_status = False
        with self.assertRaisesRegex(ValueError, "Driver is not available"):
            self.system.schedule_trip(
                "R1", "V1", "D1", self.trip.departure_time + timedelta(days=2),
                self.trip.arrival_time + timedelta(days=2), "DP1",
            )

    def test_trip_lifecycle_updates_vehicle_and_driver(self):
        self.system.start_trip("T1")
        self.assertEqual(self.system.trips["T1"].status, TripStatus.IN_PROGRESS)
        self.assertFalse(self.system.drivers["D1"].availability_status)
        self.system.complete_trip("T1")
        self.assertEqual(self.system.trips["T1"].status, TripStatus.COMPLETED)
        self.assertEqual(self.system.vehicles["V1"].mileage_km, 160)
        self.assertEqual(self.system.vehicles["V1"].status.value, "available")
        self.assertTrue(self.system.drivers["D1"].availability_status)

    def test_trip_cancel_method(self):
        self.trip.cancel()
        self.assertEqual(self.trip.status, TripStatus.CANCELLED)
        with self.assertRaisesRegex(ValueError, "cannot be cancelled"):
            self.trip.cancel()

    def test_json_round_trip_preserves_domain_objects(self):
        booking = self.system.book_trip("P1", "T1")
        self.system.process_payment(booking.booking_id, PaymentMethod.CARD)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transport.json"
            self.system.save(path)
            restored = TransportSystem.load(path)
        self.assertIsInstance(restored.vehicles["V1"], Bus)
        self.assertEqual(restored.trips["T1"].departure_time, self.trip.departure_time)
        self.assertEqual(restored.trips["T1"].dispatcher_id, "DP1")
        self.assertEqual(restored.fleets["F1"].vehicle_ids, ["V1"])
        self.assertEqual(len(restored.routes["R1"].stops), 2)
        self.assertEqual(restored.bookings[booking.booking_id].ticket.ticket_number,
                         booking.ticket.ticket_number)
        self.assertEqual(next(iter(restored.payments.values())).status, PaymentStatus.PAID)


if __name__ == "__main__":
    unittest.main()
