-- MySQL Initialization Script for Bookstore Microservices
-- Creates all required databases for MySQL services

CREATE DATABASE IF NOT EXISTS staff_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS cart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ship_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS comment_rate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS apigateway_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant all privileges to bookstore user
GRANT ALL PRIVILEGES ON staff_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON cart_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON ship_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON comment_rate_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON apigateway_db.* TO 'root'@'%';

FLUSH PRIVILEGES;
