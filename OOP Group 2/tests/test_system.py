import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

from transport_system import (
    BookingStatus, Bus, Driver, Passenger, PaymentMethod, PaymentStatus,
    Route, TransportSystem, TripStatus,
)


class TransportSystemTests(unittest.TestCase):
    def setUp(self):
        self.system = TransportSystem()
        self.system.add_passenger(Passenger("P1", "Amina Njeri", "+254700000001"))
        self.system.add_passenger(Passenger("P2", "Brian Otieno", "+254700000002"))
        self.system.add_driver(Driver("D1", "J. Kamau", "+254700000003",
                                      license_number="DL-1",
                                      license_expiry=date.today() + timedelta(days=365),
                                      years_experience=5))
        self.system.add_vehicle(Bus("V1", "KDA 123A", "Isuzu", "NQR", 2,
                                     has_air_conditioning=True, luggage_capacity_kg=500))
        self.system.add_route(Route("R1", "Nairobi", "Nakuru", 160, 150, 850.0))
        start = datetime.now().replace(second=0, microsecond=0) + timedelta(days=2)
        self.trip = self.system.schedule_trip("R1", "V1", "D1", start,
                                              start + timedelta(hours=3), trip_id="T1")

    def test_booking_assigns_distinct_seats_and_cancel_releases_seat(self):
        first = self.system.book_trip("P1", "T1")
        second = self.system.book_trip("P2", "T1")
        self.assertEqual((first.seat_number, second.seat_number), (1, 2))
        self.assertEqual(self.system.available_seats("T1"), [])
        self.system.cancel_booking(first.booking_id)
        replacement = self.system.book_trip("P2", "T1", seat_number=1)
        self.assertEqual(replacement.seat_number, 1)

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
        self.system.cancel_booking(booking.booking_id)
        self.assertEqual(payment.status, PaymentStatus.REFUNDED)
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

    def test_rejects_expired_driver_license(self):
        self.system.drivers["D1"].license_expiry = date.today() - timedelta(days=1)
        departure = datetime.now() + timedelta(days=3)
        with self.assertRaisesRegex(ValueError, "license"):
            self.system.schedule_trip("R1", "V1", "D1", departure,
                                      departure + timedelta(hours=2))

    def test_rejects_overlapping_assignment(self):
        start = self.trip.departure_time + timedelta(minutes=30)
        with self.assertRaisesRegex(ValueError, "overlapping"):
            self.system.schedule_trip("R1", "V1", "D1", start,
                                      start + timedelta(hours=1))

    def test_trip_lifecycle_updates_vehicle_and_driver(self):
        self.system.start_trip("T1")
        self.assertEqual(self.system.trips["T1"].status, TripStatus.IN_PROGRESS)
        self.assertFalse(self.system.drivers["D1"].availability_status)
        self.system.complete_trip("T1")
        self.assertEqual(self.system.vehicles["V1"].mileage_km, 160)
        self.assertTrue(self.system.drivers["D1"].availability_status)

    def test_json_round_trip_preserves_domain_objects(self):
        booking = self.system.book_trip("P1", "T1")
        self.system.process_payment(booking.booking_id, PaymentMethod.CARD)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transport.json"
            self.system.save(path)
            restored = TransportSystem.load(path)
        self.assertIsInstance(restored.vehicles["V1"], Bus)
        self.assertEqual(restored.trips["T1"].departure_time, self.trip.departure_time)
        self.assertEqual(restored.bookings[booking.booking_id].ticket.ticket_number,
                         booking.ticket.ticket_number)
        self.assertEqual(next(iter(restored.payments.values())).status, PaymentStatus.PAID)


if __name__ == "__main__":
    unittest.main()
