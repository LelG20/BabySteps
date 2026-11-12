-- Run this script in phpMyAdmin to create the local portfolio database.
CREATE DATABASE IF NOT EXISTS babystep_portfolio
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE babystep_portfolio;

-- Each submitted contact message becomes one row in this table.
CREATE TABLE IF NOT EXISTS contact_messages (
    -- AUTO_INCREMENT gives each message a unique number automatically.
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    -- Save the time of the submission automatically.
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_contact_messages_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
