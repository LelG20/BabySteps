# Run the contact form with XAMPP

This class-project setup stores contact messages in a local MySQL database. It does not send email.

1. Copy the `BabySteps` folder into XAMPP's `htdocs` directory. For example, the page should be at `C:\xampp\htdocs\BabySteps\PortfolioSite\lelg.html` on Windows.
2. Open the XAMPP Control Panel and start **Apache** and **MySQL**.
3. Open `http://localhost/phpmyadmin/` in your browser.
4. In phpMyAdmin, choose **Import**, select `PortfolioSite/database.sql`, and run the import. This creates the `babystep_portfolio` database and the `contact_messages` table.
5. Open `http://localhost/BabySteps/PortfolioSite/lelg.html`, fill in the contact form, and submit it.
6. To view saved messages, open the `babystep_portfolio` database and select the `contact_messages` table in phpMyAdmin.

The PHP handler uses PDO prepared statements and validates the submitted fields on the server. `config.php` uses the common local XAMPP defaults (`root` with a blank password). If your MySQL account has a password or a different username, update `config.php` for your local setup.

Keep this configuration for local class use only. Do not publish the default root/blank-password settings to a public server or commit real database passwords to a public repository.
