# Transport Management System - OOP Analysis and UML Design

**BIT223 Object-Oriented Programming I | Group 2**

## Group members
- Mitchel, Mitch Kioko Maungu
- Gichuhi, Maryhope Wanjiru
- Wangai, Jesse Barnabs
- James Gyabi
- Leon Gikonyo
- Munene, Aaron Nderitu
- Ndegwa, Wanjiku Wendy
- Miano, Jackson Ndambiri

## About
An object-oriented analysis of a road passenger transport company: fleet, drivers, routes, trips, bookings, tickets and payments. The design follows the required process:
Scenario > Questions > Objects > Classes > Attributes > Methods > Inheritance > Relationships > Multiplicity > UML > Presentation.

## Files
| File | What it is |
|---|---|
| `transport_management_system.drawio` | Editable UML class diagram (open in https://app.diagrams.net) |
| `transport_management_system_uml.png` | Full-resolution image of the diagram |

## Design summary
- **15 classes**, 2 abstract (`Person`, `Vehicle`)
- **Inheritance (5):** Passenger, Driver, Dispatcher extend Person; Bus, Minibus extend Vehicle
- **Associations (7):** Passenger-Booking, Booking-Trip, Trip-Route, Trip-Vehicle, Driver-Trip, Dispatcher-Trip, Booking-Payment
- **Aggregations (2):** Route-Stop, Fleet-Vehicle
- **Compositions (2):** Booking-Ticket, Vehicle-MaintenanceRecord

## Assumptions
- Passenger transport only; freight is out of scope
- One booking is one seat on one trip
- One driver and one vehicle per trip
- Payment by M-Pesa, card or cash
- A fleet is one depot's group of vehicles
