# Transport Management System — Python

**BIT223 Object-Oriented Programming I | Group 2**

This project is a Python prototype for basic passenger transport operations. It represents people, vehicles, routes, trips, bookings, payments, fleets, tickets, and maintenance records with classes. The current user interface is a text-based console menu; it is not connected to a graphical UI.

Requires Python 3.10 or newer. It uses only the Python standard library.

## Run the application

```bash
cd "OOP Group 2"
python -m transport_system
```

Use the menu to add a fleet, bus, passenger, driver, dispatcher, and route. A route must have at least two stops. Then schedule a trip, book a seat, record a simulated payment, and start or complete the trip. Choose **Save and exit** to store the current data in `transport_data.json`.

Payments are recorded locally only; no payment provider is contacted. Route distance, duration, and fare use sample values, and the CLI schedules trips for tomorrow with a two-hour duration.

## Run the tests

```bash
cd "OOP Group 2"
python -m unittest discover -s tests -v
```

## Project files

- `transport_system/models.py` — domain classes, inheritance, and simple object behavior.
- `transport_system/system.py` — collections, scheduling, booking, payment, lifecycle, maintenance, and JSON save/load.
- `transport_system/cli.py` — console menu and user input.
- `tests/test_system.py` — tests for booking, abstract classes, scheduling, payment, lifecycle, and persistence.
- `transport_management_system.drawio` — editable class diagram.
- `transport_management_system_uml.png` — UML diagram image.

## Main design rules

`Person` and `Vehicle` are abstract base classes. Passenger, Driver, Dispatcher, Bus, and Minibus are concrete types. Each vehicle must be added to one fleet. Each trip has one route, vehicle, driver, and dispatcher. Each route has at least two stops. A booking reserves one seat and may contain a ticket. The vehicle keeps its maintenance history.
