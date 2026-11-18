# Transport Management System — Python

**BIT223 Object-Oriented Programming I | Group 2**

This is a Python console prototype for passenger transport operations. It uses the UML domain classes for passengers, drivers, dispatchers, buses, minibuses, fleets, routes, stops, trips, bookings, tickets, payments, and maintenance records. CSV files are the program's main input and storage format.

It requires Python 3.10 or newer and uses only the Python standard library.

## Run the two programs

The project has two separate console programs. Run them from the `OOP Group 2` folder.

For staff operations, run:

```bash
python internal_management.py
```

This menu is for adding and managing fleets, buses, minibuses, passengers, drivers, dispatchers, routes, and trips. It also handles trip operations, maintenance, driver issues, dispatcher reports, and staff booking cancellation. Choose **12. View all loaded records** to inspect the CSV data.

For customers, run:

```bash
python customer_booking.py
```

This menu lets customers browse scheduled trips with available seats, book a seat, view their bookings, record a simulated payment, or cancel their own booking. When booking, a customer can enter a name and phone number; the phone number is used to find their bookings later. If the phone number is new, the program creates a passenger record.

In PyCharm, create two Python run configurations, with the working directory set to the `OOP Group 2` folder: one using `internal_management.py` as the script path and another using `customer_booking.py`. Do not run `transport_system/__main__.py` as a script; it uses a package-relative import. The older `python -m transport_system` command remains an alias for the internal menu.

Both programs load and save the same CSV files in the project's `data/` folder. Successful staff changes and customer bookings, payments, and cancellations are written immediately; the menu prints the folder path after saving. **0. Save CSV files and exit** also saves before closing. Check the `data/` folder beside `transport_system/` in PyCharm's project tree, not the current working directory or a separate `data` folder. Run only one program at a time; simultaneous runs could overwrite newer changes with an older in-memory copy. The customer menu does not expose staff-management actions, but the shared local files and phone-number lookup are not an authentication or security system. This is a classroom prototype, not a production booking service.

## Demonstration flow

The prefilled files now provide a fuller demonstration: 12 passengers, 6 drivers, 3 dispatchers, 3 fleets, 7 vehicles, 7 routes, 10 scheduled trips, and 26 bookings with linked tickets. Payment history includes paid and refunded examples, and the vehicles have completed maintenance records and driver issue notes. A walkthrough of both programs:

1. Start `internal_management.py`; choose **12** to view the loaded data and **9** to list sample trips.
2. Choose **0** to save and exit the internal program.
3. Start `customer_booking.py`; choose **1** to browse trips with open seats.
4. Choose **2** to book a trip. Enter a name and phone number, then choose a seat or leave the seat prompt blank for the first available one.
5. Choose **3** to view the customer's bookings, or **4** to record a simulated payment.
6. Choose **0** to save and exit. Reopen the internal program and choose **12** to see the booking in the shared CSV data.

The sample trips use dates in February 2027 so customers can see several upcoming options; bookings, tickets, and payment records are seeded as demonstration history. Payments are local demonstration records only; no bank or mobile-money provider is contacted.

## CSV files and relationships

Each concrete class has a separate file. The abstract base classes `Person` and `Vehicle` do not have their own files; their concrete types are stored separately.

| CSV file | Records stored / important links |
|---|---|
| `passengers.csv` | Passenger profile and loyalty information. |
| `drivers.csv` | Driver profile, license, availability, and experience. |
| `driver_issues.csv` | Driver issue descriptions linked with `driver_id`. |
| `dispatchers.csv` | Dispatcher profile, employee ID, and shift. |
| `fleets.csv` | Fleet IDs, names, and depot locations. |
| `buses.csv` | Bus details and its `fleet_id`. |
| `minibuses.csv` | Minibus details and its `fleet_id`. |
| `routes.csv` | Route details, distance, duration, and fare. |
| `stops.csv` | Stops linked to a route with `route_id`. Each route needs at least two stops. |
| `trips.csv` | Trip status and links to one route, vehicle, driver, and dispatcher by ID. |
| `bookings.csv` | Seat reservation linked to one passenger and one trip. |
| `tickets.csv` | Optional ticket linked to its booking by `booking_id`. |
| `payments.csv` | Payment record linked to its booking by `booking_id`. |
| `maintenance_records.csv` | Service history linked to its vehicle by `vehicle_id`. |

IDs act as foreign keys between the files. For example, `trips.csv` contains `route_id`, `vehicle_id`, `driver_id`, and `dispatcher_id`; `bookings.csv` contains `passenger_id` and `trip_id`. Keep referenced IDs consistent when editing CSV files manually.

## Main design rules

- A vehicle belongs to one fleet.
- Each trip has one route, vehicle, driver, and dispatcher.
- Each route has at least two stops.
- A booking reserves one seat on a scheduled trip and may have one ticket.
- A vehicle owns its maintenance history.
- Cancelling a paid booking records a refund in the local payment status.
- Starting/completing a trip updates trip status, driver availability, vehicle status, and mileage.

## Existing JSON data from the earlier version

The CSV version does not load or overwrite the old `transport_data.json`. If you previously saved data using the JSON version, keep a backup of that file before switching. The new program loads the prefilled CSVs in `data/` instead.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Project files

- `internal_management.py` — standalone staff-management launcher.
- `customer_booking.py` — standalone customer-booking launcher.
- `transport_system/models.py` — UML domain classes, relationships, and object methods.
- `transport_system/system.py` — booking, scheduling, payment, lifecycle, and maintenance rules.
- `transport_system/csv_storage.py` — reads and writes the separate CSV files.
- `transport_system/cli.py` — internal staff menu and data viewer.
- `transport_system/customer_cli.py` — customer trip browsing, booking, and booking management.
- `data/*.csv` — prefilled input files and saved application data.
- `tests/test_system.py` — behavior, UML methods, and CSV round-trip tests.
- `transport_management_system.drawio` and `transport_management_system_uml.png` — editable and rendered UML diagrams.
