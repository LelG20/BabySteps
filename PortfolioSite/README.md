# Leon Gikonyo — Student Portfolio

A beginner portfolio project built with HTML, CSS, JavaScript, PHP, and MySQL. It presents Leon's background, skills, and projects, and includes an interactive mobile menu, a learning-tip button, and a contact form that saves messages to a local database.

## What is in this folder?

| File | Purpose |
| --- | --- |
| `lelg.html` | The portfolio page: navigation, introduction, About, Skills, Projects, Contact, and footer sections. It links the stylesheet and the external JavaScript file. |
| `styles.css` | The visual design, including colors, typography, layout, contact-form styling, and responsive rules for smaller screens. |
| `script.js` | Beginner-level browser interactions: the mobile menu, rotating learning tips, and client-side contact-form validation. |
| `contact.php` | Receives the contact form's POST request, checks the submitted values again on the server, and inserts a message into MySQL. |
| `config.php` | Local database connection settings used by `contact.php`. The included values are common XAMPP defaults. |
| `database.sql` | Creates the `babystep_portfolio` database and its `contact_messages` table. Import it with phpMyAdmin. |
| `SETUP-XAMPP.md` | A short XAMPP setup checklist. |

## How the page works

### HTML and CSS

`lelg.html` uses semantic sections with IDs so the navigation links can jump to About, Skills, Projects, and Contact. `styles.css` keeps the original clean portfolio design and uses a mobile breakpoint at 680 pixels. On smaller screens, the project cards and contact form stack vertically, and the navigation can be opened with the Menu button. The stylesheet also respects the visitor's reduced-motion preference.

### JavaScript interactions

The HTML loads `script.js` with `defer`, so the browser runs the script after it has read the page. The script uses DOM selection methods such as `querySelector` and `querySelectorAll`, and responds to clicks, form submissions, typing, keyboard input, and window resizing.

- **Mobile menu:** The Menu button opens and closes the navigation. It also closes after a visitor chooses a link, presses Escape, or widens the browser to desktop size. Its `aria-expanded` and accessible label update as it changes state.
- **Learning tips:** The “Show a learning tip” button updates the page with the next tip each time it is clicked.
- **Contact validation:** Before the form is submitted, JavaScript checks that required fields are filled in and that the email address is valid. It shows a message, marks the field, and moves focus to the field that needs attention. After the input is corrected, the message clears.

The JavaScript improves the visitor experience, but it is not the only validation. `contact.php` checks the form data again on the server before saving it.

### Contact form and database

The contact form in `lelg.html` sends the visitor's name, email, subject, and message to `contact.php` using an HTTP POST request. PHP connects to MySQL with PDO and a prepared SQL statement, then stores the values in the `contact_messages` table. Each record also receives a submission timestamp.

This class-project form saves messages in the database; it **does not send email**. View saved submissions by opening the `babystep_portfolio` database and selecting `contact_messages` in phpMyAdmin.

## Run it locally with XAMPP

PHP pages must be served by Apache. Opening `lelg.html` directly as a file will show the front end, but the PHP form handler will not run that way.

1. Copy the `BabySteps` repository folder into XAMPP's `htdocs` folder. For example, on Windows the portfolio page should be at `C:\xampp\htdocs\BabySteps\PortfolioSite\lelg.html`.
2. Open the XAMPP Control Panel and start **Apache** and **MySQL**.
3. Visit `http://localhost/phpmyadmin/`.
4. In phpMyAdmin, choose **Import**, select `PortfolioSite/database.sql`, and run the import. It creates the database and table.
5. Open `http://localhost/BabySteps/PortfolioSite/lelg.html` in your browser.
6. Submit a test message, then use phpMyAdmin to confirm it appears in `babystep_portfolio` → `contact_messages`.

If your local MySQL username or password is different from the XAMPP defaults in `config.php`, update that file for your local machine. See [`SETUP-XAMPP.md`](SETUP-XAMPP.md) for the shorter setup checklist.

## Manual test checklist

- On a desktop-width window, confirm the navigation links appear in the header.
- At a phone-width window (680 pixels or narrower), open and close the Menu button. Confirm a menu link, the Escape key, and returning to desktop width close the menu.
- Click “Show a learning tip” twice and confirm that the displayed text changes.
- Submit the contact form empty and confirm it asks for the required fields.
- Enter an invalid email address and confirm it is rejected.
- Enter valid details and submit while Apache and MySQL are running; confirm the success message and check the database table.

## Learning concepts demonstrated

This project demonstrates semantic HTML and page sections, external CSS, responsive media queries, an external JavaScript file, DOM selection, event listeners, functions, arrays, conditionals, dynamic text updates, client-side and server-side validation, PHP form handling, PDO database connections, prepared SQL statements, and a MySQL table.

## Assignment requirements checklist

| Requirement | Where it is demonstrated |
| --- | --- |
| 1. External JavaScript file | `lelg.html` loads `script.js` with the `defer` attribute. |
| 2. Interactive navigation/menu | `script.js` opens and closes the mobile Menu button, updates its ARIA state, and closes the menu after link selection, Escape, or resizing to desktop. |
| 3. Dynamic content button | The “Show a learning tip” button is connected to `showNextLearningTip()` in `script.js`. |
| 4. Contact form with validation | `validateContactForm()` checks required fields and the email address in JavaScript; `contact.php` validates again on the server before saving. |
| 5. DOM manipulation and event listeners | `script.js` uses `querySelector()` and `querySelectorAll()`, plus click, submit, input, keydown, and resize event listeners. |
| 6. Functions and conditionals | `setMenuOpen()`, `showNextLearningTip()`, and `validateContactForm()` are functions. Their `if` statements control menu state, missing elements, and invalid form input. |
| 7. Dynamic content updates | `showNextLearningTip()` changes the learning-tip element with `textContent`; the form validator updates its status message. |
| 8. Responsive compatibility | `styles.css` uses a 680-pixel breakpoint to switch to the mobile menu and stack the layout; the manual test checklist covers desktop and phone widths. |

The project is in the [BabySteps GitHub repository](https://github.com/LelG20/BabySteps). Before submitting, run through the manual test checklist above in your local browser and XAMPP setup.

## Important local-use note

The included `config.php` uses the common local XAMPP account (`root` with a blank password) to make a classroom setup straightforward. This is for local learning only. Do not use those defaults on a public server, and never put a real database password in a public GitHub repository.
