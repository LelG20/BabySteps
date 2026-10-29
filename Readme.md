# BabySteps

BabySteps is a collection of programming and software-development assignments completed while learning to build practical projects. Each top-level folder is a separate project; use that folder's README for its detailed design notes and instructions.

## Projects

### [`GradeCalculator/`](GradeCalculator/)
A beginner Python assignment that builds up to a grade calculator. Its small scripts demonstrate variables and data types, operators, decision structures, loops, functions, and modules. The main calculator combines those ideas to calculate grade averages, while `gradecalc_improv` adds input-range checks and lists subjects with their grades.

See the [GradeCalculator README](GradeCalculator/README.md) for the assignment breakdown.

### [`OOP Group 2/`](OOP%20Group%202/)
A group Object-Oriented Programming project: a Python passenger transport management system, together with its UML class diagram and rendered diagram image. The console application covers passengers, drivers, vehicles, routes, trips, bookings, and simulated payments. It also includes automated tests.

To run it, use Python 3.10 or newer and follow the [transport-system README](OOP%20Group%202/README.md).

### [`PerformanceAnalyzer/`](PerformanceAnalyzer/)
A Python OOP program that reads student records from a CSV file, calculates class and individual performance metrics, checks scholarship eligibility, and creates a text report. The folder includes the source code, sample data, and an example generated report.

See the [PerformanceAnalyzer README](PerformanceAnalyzer/README.md) for the class design, requirements, and run instructions.

### [`PortfolioSite/`](PortfolioSite/)
A responsive personal portfolio built with HTML and CSS, with an external JavaScript file for the mobile navigation, interactive learning tips, and contact-form validation. The form submits to a PHP handler that stores messages in a MySQL database for local use with XAMPP.

Start with the [PortfolioSite README](PortfolioSite/README.md) and its [XAMPP setup checklist](PortfolioSite/SETUP-XAMPP.md). The contact form stores messages locally; it does not send email.

## Getting started

These projects are independent, so open the folder you want to explore and follow its README. The Python assignments use their own files and instructions. To run the portfolio's PHP contact form, use a local PHP/MySQL environment such as XAMPP and import `PortfolioSite/database.sql` through phpMyAdmin.
