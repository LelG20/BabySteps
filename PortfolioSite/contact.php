<?php
declare(strict_types=1);

function showResult(int $status, string $heading, string $message): void
{
    http_response_code($status);
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title><?= htmlspecialchars($heading, ENT_QUOTES, 'UTF-8') ?> | Leon Gikonyo</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <main>
            <section class="contact-section" aria-labelledby="result-heading">
                <p class="eyebrow">04 / Contact</p>
                <h2 id="result-heading"><?= htmlspecialchars($heading, ENT_QUOTES, 'UTF-8') ?></h2>
                <p><?= htmlspecialchars($message, ENT_QUOTES, 'UTF-8') ?></p>
                <a class="button" href="lelg.html#contact">Back to the portfolio</a>
            </section>
        </main>
    </body>
    </html>
    <?php
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    showResult(405, 'Method not allowed', 'Please send your message using the contact form.');
}

function postedText(string $key): string
{
    $value = $_POST[$key] ?? '';
    return is_string($value) ? trim($value) : '';
}

function textLength(string $value): int
{
    return function_exists('mb_strlen') ? mb_strlen($value, 'UTF-8') : strlen($value);
}

$name = postedText('name');
$email = postedText('email');
$subject = postedText('subject');
$message = postedText('message');

if ($name === '' || $email === '' || $subject === '' || $message === '') {
    showResult(422, 'Please complete every field', 'Go back to the form and fill in your name, email, subject, and message.');
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)
    || textLength($name) > 120
    || textLength($email) > 254
    || textLength($subject) > 200
    || textLength($message) > 5000) {
    showResult(422, 'Please check your details', 'Use a valid email address and keep each field within its listed length limit.');
}

$config = require __DIR__ . '/config.php';
$dsn = sprintf(
    'mysql:host=%s;dbname=%s;charset=%s',
    $config['host'],
    $config['database'],
    $config['charset']
);

try {
    $pdo = new PDO($dsn, $config['username'], $config['password'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]);

    $statement = $pdo->prepare(
        'INSERT INTO contact_messages (name, email, subject, message)
         VALUES (:name, :email, :subject, :message)'
    );
    $statement->execute([
        'name' => $name,
        'email' => $email,
        'subject' => $subject,
        'message' => $message,
    ]);
} catch (PDOException $exception) {
    error_log('Portfolio contact form database error: ' . $exception->getMessage());
    showResult(500, 'Message could not be saved', 'Check that Apache and MySQL are running and that database.sql has been imported in phpMyAdmin.');
}

showResult(200, 'Thanks for reaching out.', 'Your message has been saved successfully.');
