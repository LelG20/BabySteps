<?php
declare(strict_types=1);

// Local XAMPP defaults for this class project. Do not publish this file or
// reuse the blank-password root account on a public server.
return [
    'host' => getenv('DB_HOST') ?: '127.0.0.1',
    'database' => getenv('DB_NAME') ?: 'babystep_portfolio',
    'username' => getenv('DB_USER') ?: 'root',
    'password' => getenv('DB_PASS') ?: '',
    'charset' => 'utf8mb4',
];
