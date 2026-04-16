-- PostgreSQL Initialization Script for Bookstore Microservices
-- Creates all required databases for PostgreSQL services

CREATE DATABASE manager_db;
CREATE DATABASE customer_db;
CREATE DATABASE order_db;
CREATE DATABASE pay_db;
CREATE DATABASE product_db;
CREATE DATABASE ai_db;

-- Grant privileges to bookstore user
GRANT ALL PRIVILEGES ON DATABASE manager_db TO root;
GRANT ALL PRIVILEGES ON DATABASE customer_db TO root;
GRANT ALL PRIVILEGES ON DATABASE order_db TO root;
GRANT ALL PRIVILEGES ON DATABASE pay_db TO root;
GRANT ALL PRIVILEGES ON DATABASE product_db TO root;
GRANT ALL PRIVILEGES ON DATABASE ai_db TO root;
