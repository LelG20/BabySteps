# GROUP 2: TRANSPORT SYSTEM WALKTHROUGH

This script follows a clear path from start (the problem) to finish (the code realization).

## 1. Maryhope — Introduction and System Entry
**Goal:** Show how we start the system to solve the double-booking problem.

“We built this system to stop manual errors like overbooking and missing tickets. Everything starts in `cli.py`. My part shows the system menu where a manager can add fleets, vehicles, and passengers. When we choose 'Add Fleet' or 'Add Bus', the CLI calls our `TransportSystem` coordinator in `system.py`. This is the 'Scope' of our project: we handle the main pieces a transport company needs every day.”

**Show:** Open `cli.py` and show the `while True` loop and the menu options.

## 2. Gyabi — Domain Models (People and Places)
**Goal:** Show how real-world things become Python classes.

“Once the system is running, we need to represent the real objects. In `models.py`, I’ve defined `Person` and `Vehicle` as **Abstract Base Classes**. This is important because you can't have a generic 'person' in our system—it must be a `Passenger`, `Driver`, or `Dispatcher`. We also have `Stop` and `Route` classes. Notice that a `Route` must have at least two stops; we enforce that rule right inside the class.”

**Show:** Open `models.py`. Point to `@dataclass class Person(ABC)` and `class Route`.

## 3. Jackson — Object Attributes and Lifecycle
**Goal:** Show how data is stored and how objects change over time.

“Classes are just blueprints until they have data. I’m showing the `Trip` and `Booking` classes. A `Trip` stores the journey state in **attributes** like `departure_time` and `status`. We use **methods** like `start()` and `complete()` to change that state. For example, a trip can't start unless it is scheduled. This ensures our data always stays consistent with what’s happening on the road.”

**Show:** Open `models.py`. Point to `class Trip` and its `start()` method.

## 4. Aaron — Inheritance and Relationships
**Goal:** Show how classes are connected (IS-A and HAS-A).

“Now we connect the pieces. We use **Inheritance** so that `Bus` and `Minibus` 'are-a' kind of `Vehicle`. They get all the common fields like registration number for free but can add their own, like air conditioning. We also have **Composition**: a `Booking` owns its `Ticket`, and a `Vehicle` owns its `maintenance_history`. When you create a booking, the ticket is created right along with it.”

**Show:** Open `models.py`. Point to `class Bus(Vehicle)` and the `ticket` field in `class Booking`.

## 5. Mitch — Multiplicity and Business Rules
**Goal:** Show how we enforce the 'How Many' rules from our UML.

“The UML says a vehicle belongs to exactly one fleet. In `system.py`, I’ve implemented the `add_vehicle` method to enforce this. If you try to add a bus to a second fleet, the system throws an error. I also coordinate the `schedule_trip` method, which makes sure every journey has exactly one route, one vehicle, one driver, and one dispatcher. This is how the lines and numbers on our diagram become real code logic.”

**Show:** Open `system.py`. Point to `add_vehicle` and the fleet check.

## 6. Jesse — UML to Code Realization
**Goal:** Trace a single feature from the diagram all the way through the layers.

“I’m bringing it all together by tracing a 'Booking'. When a passenger wants a seat, the CLI calls `book_trip` in my section of `system.py`. The system checks the IDs, finds the fare from the `Route`, and creates a new `Booking` object. Finally, we use **Persistence** to save all these objects into a `transport_data.json` file, so the data is still there the next time you open the program.”

**Show:** Open `system.py`. Point to `book_trip` and the `save()` method.

## 7. Leon — Conclusions and Design Choices
**Goal:** Summarize the design decisions and prototype limits.

“To finish, our design makes some key choices to keep things simple. We use **Simulated Payments** in `process_payment`, which updates our local records without needing a real bank connection. We decided that seats and fares are attributes, not separate classes, because they don't need their own behavior. This prototype proves that our UML design works and is ready to be expanded into a full database-backed application.”

**Show:** Open `system.py`. Point to `process_payment`. Explain why it just sets the status to `PAID`.
