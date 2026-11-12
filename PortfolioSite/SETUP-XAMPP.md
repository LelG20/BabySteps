# Run the contact form with XAMPP

This class-project setup stores contact messages in a local MySQL database. It does not send email.

The form requires a name, email address, and message. The subject is optional. The email field accepts an email address format; the name and subject are text fields, and the message is a text area.

1. Copy the `BabySteps` folder into XAMPP's `htdocs` directory. For example, the page should be at `C:\xampp\htdocs\BabySteps\PortfolioSite\lelg.html` on Windows.
2. Open the XAMPP Control Panel and start **Apache** and **MySQL**.
3. Open `http://localhost/phpmyadmin/` in your browser.
4. In phpMyAdmin, choose **Import**, select `PortfolioSite/database.sql`, and run the import. This creates the `babystep_portfolio` database and the `contact_messages` table.
5. Open `http://localhost/BabySteps/PortfolioSite/lelg.html`, fill in the contact form, and submit it.
6. To view saved messages, open the `babystep_portfolio` database and select the `contact_messages` table in phpMyAdmin.

The PHP handler uses PDO prepared statements and validates the submitted fields on the server. `config.php` uses the common local XAMPP defaults (`root` with a blank password). If your MySQL account has a password or a different username, update `config.php` for your local setup.

## Troubleshooting: PHP source appears in the browser

If the browser shows code beginning with `<?php` after you submit the form, PHP is not being executed. Start **Apache** in the XAMPP Control Panel, then open the page using `http://localhost/BabySteps/PortfolioSite/lelg.html`. Do not open the HTML with a `file://` address or use VS Code Live Server; those do not run this PHP handler. When the page is served correctly, submitting the form should show a styled success or validation message—not PHP source code.

Keep this configuration for local class use only. Do not publish the default root/blank-password settings to a public server or commit real database passwords to a public repository.
