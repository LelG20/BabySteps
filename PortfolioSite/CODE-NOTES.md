# PortfolioSite — Code Notes for Beginners

These notes explain how the portfolio works so you can read the code and describe it in class. Start with the visitor's journey, then look at one file at a time.

## The whole project in one picture

```text
Visitor's browser
  lelg.html  -> page content and contact form
      |        styles.css styles the page
      |        script.js adds menu, tip button, and form checks
      |
      +-- form sends a POST request to contact.php
                  | checks the submitted data again
                  | reads connection settings from config.php
                  | connects to MySQL using PDO
                  +-- saves one row in contact_messages
                         database.sql creates the database and table
```

The browser runs HTML, CSS, and JavaScript. PHP runs on the web server (XAMPP Apache in this class project), not inside the browser. MySQL stores the submitted messages.

## Read the files in this order

1. **`lelg.html` — page structure and content.** This is the page the visitor opens. It contains the navigation, introduction, About, Skills, Projects, and Contact sections. The `id` on a section gives the navigation a place to jump to; for example, `href="#about"` jumps to `id="about"`.
2. **`styles.css` — appearance and responsive layout.** It sets the colors, fonts, spacing, grids, form appearance, and small-screen layout. Its `@media (max-width: 680px)` rule changes the layout on narrow screens.
3. **`script.js` — browser interactions.** It listens for clicks and form events, selects page elements, changes the learning tip, opens the mobile menu, and checks required form fields and email format.
4. **`database.sql` — database setup.** Import it once in phpMyAdmin to create the `babystep_portfolio` database and `contact_messages` table.
5. **`config.php` — connection settings.** It gives PHP the MySQL host, database name, username, password, and character set. The defaults are for a local XAMPP class setup.
6. **`contact.php` — form processing.** Apache runs this file after the form is submitted. It validates the values, inserts them into MySQL, then returns a success or error page.

## How the contact form works, step by step

1. In `lelg.html`, each field has a `name`. These names become keys in PHP's `$_POST` data.
2. Name, email, and message have the HTML `required` attribute. Subject is optional. The email field uses `type="email"`, which gives it an email-specific browser check.
3. `script.js` listens for the form's `submit` event. It checks required fields first, then calls the browser's `checkValidity()` method for the email address. If something is wrong, `event.preventDefault()` stops the request so the page can show an error and focus the field that needs attention.
4. If those checks pass, the browser sends the fields to `contact.php` using `method="post"`. POST sends form data in the request body rather than adding it to the page URL.
5. `contact.php` checks the required fields and email again. This server-side check matters because a visitor can turn off or bypass JavaScript.
6. PHP loads `config.php` and creates a PDO connection to MySQL. A prepared SQL statement uses placeholders for the visitor's values, keeping submitted text separate from the SQL command.
7. MySQL adds a row to `contact_messages`. If the insert succeeds, PHP returns a confirmation page. If it fails, PHP shows a helpful message and writes technical database details to the server log.

The form saves messages in the local database; it does not send email. Because Subject is optional, a blank subject is stored as an empty string.

## Useful code ideas to know

### HTML: elements, IDs, classes, and forms

- An **element** is a page building block such as `<p>`, `<section>`, `<button>`, or `<input>`.
- An **ID** identifies one particular element. JavaScript uses selectors such as `#contact-form` to find it, and navigation links use IDs as destinations.
- A **class** can be reused on many elements. CSS selectors such as `.form-field` apply the same appearance to each matching element.
- A form's `action="contact.php"` says where to send it. `method="post"` says how to send it. The `name="email"` attribute identifies the field in PHP.
- `required` is the real required-field rule; the words “(required)” and “(optional)” make that rule visible to visitors.
- `novalidate` turns off the browser's default validation popups so the project can display its own messages with JavaScript. The JavaScript still uses the email field's built-in `checkValidity()` method.

### CSS: selectors, variables, and responsive design

- A **selector** chooses which elements to style. For example, `.contact-form` selects the form by class, and `.form-field input` selects inputs inside a form field.
- Values starting with `--`, such as `--accent`, are CSS **custom properties** (variables). `var(--accent)` reuses the same color in multiple rules.
- **Flexbox** and **Grid** arrange content. The desktop contact form uses two grid columns; the mobile media query changes it to one.
- A **media query** applies styles only when a condition is true. Here, `max-width: 680px` means “when the screen is 680 pixels wide or narrower.”
- `:focus-visible` styles the control a keyboard user is currently using. The reduced-motion query respects a visitor's device preference to minimize animation.

### JavaScript: selection, functions, conditions, and events

- `document.querySelector("#menu-toggle")` finds the first element with that ID. `querySelectorAll("[required]")` finds all elements with the `required` attribute.
- A **variable** stores a value. `const` is used for references that are not reassigned; `let` is used for `nextTipIndex` because that number changes.
- A **function** is a named set of steps. `setMenuOpen()` updates the menu, `showNextLearningTip()` displays a tip, and `validateContactForm()` checks the form.
- An **if statement** chooses what to do based on a condition. For example, the form stops submission if a required value is missing or the email is invalid.
- An **event listener** waits for an action. The code listens for `click`, `submit`, `input`, `keydown`, and window `resize` events.
- `textContent` changes text safely without treating it as HTML. The `%` (remainder) operator wraps the learning-tip index back to zero after the last tip.
- `aria-expanded`, `aria-label`, and `aria-live` provide information to assistive technologies such as screen readers.

### PHP and MySQL: server-side work

- `$_SERVER['REQUEST_METHOD']` tells PHP how the page was requested. This handler accepts POST submissions.
- `$_POST` contains submitted form values. `postedText()` checks that a value is text and trims extra spaces around it.
- `filter_var(..., FILTER_VALIDATE_EMAIL)` checks the email format on the server. The length checks match the maximum sizes set on the HTML fields.
- **PDO** is PHP's database connection interface. The DSN describes the database host, name, and character set.
- A **prepared statement** contains placeholders such as `:email`. `execute()` supplies the actual visitor values for those placeholders.
- `try`/`catch` lets the handler respond if the database connection or insert fails. `htmlspecialchars()` safely displays text in the result page.
- In `database.sql`, `NOT NULL` means a value is needed, `AUTO_INCREMENT` assigns a new ID, and `DEFAULT CURRENT_TIMESTAMP` records when a row was created.

## Running and testing it

1. Put the whole `BabySteps` folder under XAMPP's `htdocs` directory.
2. Start Apache and MySQL in the XAMPP Control Panel.
3. Import `database.sql` through `http://localhost/phpmyadmin/`.
4. Open `http://localhost/BabySteps/PortfolioSite/lelg.html`—not a `file://` URL or a static preview server.
5. Test the menu at desktop and phone widths, click the learning-tip button more than once, try an empty form, try an invalid email, and then submit valid data with Subject left blank.
6. Check phpMyAdmin's `babystep_portfolio` → `contact_messages` table to see the saved row.

If the browser prints PHP source (for example, it shows `<?php`), Apache/PHP is not handling that URL. Start XAMPP Apache and use the `http://localhost/...` page address. More setup help is in [`SETUP-XAMPP.md`](SETUP-XAMPP.md).

## Short class explanation

> “This is a responsive student portfolio made with HTML, CSS, and JavaScript. The HTML gives the page its sections and contact form; the CSS styles the page and rearranges it for mobile. JavaScript makes the menu interactive, cycles through learning tips, and checks required fields and email format. When the form is valid, it sends the data to a PHP handler. PHP validates it again and uses PDO with a prepared statement to save it in a MySQL table. The project runs locally in XAMPP.”

## Questions you may be asked

**Why validate in both JavaScript and PHP?** JavaScript gives quick feedback, but server-side validation is still needed because browser checks can be bypassed.

**Why use a prepared statement?** It keeps user-entered text separate from SQL instructions and is the safe standard way to insert form data.

**Why is Subject optional?** It is useful context but not necessary to contact the portfolio owner. The HTML and PHP both treat it as optional.

**Why does PHP need XAMPP?** PHP must be run by a server. A browser can display the HTML file directly, but it cannot execute the PHP handler by itself.
