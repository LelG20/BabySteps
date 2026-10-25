# Transport Management System — Python Implementation

**BIT223 Object-Oriented Programming I | Group 2**

This folder contains the UML analysis and an initial working Python implementation of the passenger transport management system. The implementation follows the existing class diagram and assumptions: passenger transport only, one seat per booking, one driver and vehicle per trip, and payment by M-Pesa, card, or cash.

## Run the console application

Requires Python 3.10 or newer; there are no third-party dependencies.

```bash
cd "OOP Group 2"
python -m transport_system
```

The CLI can add passengers, drivers, buses and routes; schedule trips; list trips; book/cancel seats; and record payments. Payment processing is simulated: no real M-Pesa, card, or cash transactions are made. Data is saved to `transport_data.json` in the current working directory when an operation completes or the app exits. Keep this generated data file private if it contains real personal information.

## Run tests

```bash
cd "OOP Group 2"
python -m unittest discover -s tests -v
```

## Project layout

- `transport_system/models.py` — UML domain classes, inheritance, and status enums.
- `transport_system/system.py` — business rules, scheduling, bookings, payments, maintenance, and JSON persistence.
- `transport_system/cli.py` — interactive command-line entry point.
- `tests/test_system.py` — tests for booking, scheduling, payment, lifecycle, and persistence.
- `transport_management_system.drawio` — editable UML class diagram (open with diagrams.net).
- `transport_management_system_uml.png` — rendered UML diagram.

The system is dependency-free and uses local JSON persistence in this initial version. It is a foundation for adding richer dispatcher workflows and a database or web interface later.

## Original project summary

### Group members
- Mitchel, Mitch Kioko Maungu
- Gichuhi, Maryhope Wanjiru
- Wangai, Jesse Barnabs
- James Gyabi
- Leon Gikonyo
- Munene, Aaron Nderitu
- Ndegwa, Wanjiku Wendy
- Miano, Jackson Ndambiri

### Design summary
- **15 classes**, 2 abstract (`Person`, `Vehicle`).
- **Inheritance (5):** `Passenger`, `Driver`, and `Dispatcher` extend `Person`; `Bus` and `Minibus` extend `Vehicle`.
- **Associations (7):** Passenger-Booking, Booking-Trip, Trip-Route, Trip-Vehicle, Driver-Trip, Dispatcher-Trip, Booking-Payment.
- **Aggregations (2):** Route-Stop, Fleet-Vehicle.
- **Compositions (2):** Booking-Ticket, Vehicle-MaintenanceRecord.

### Assumptions
- Passenger transport only; freight is out of scope.
- One booking is one seat on one trip.
- One driver and one vehicle per trip.
- Payment by M-Pesa, card or cash.
- A fleet is one depot's group of vehicles.
