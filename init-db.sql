-- Create databases and users

-- Product DB
CREATE USER product_user WITH PASSWORD 'product_pass';
CREATE DATABASE product_db OWNER product_user;

-- Customer DB
CREATE USER customer_user WITH PASSWORD 'customer_pass';
CREATE DATABASE customer_db OWNER customer_user;

-- Inventory DB
CREATE USER inventory_user WITH PASSWORD 'inventory_pass';
CREATE DATABASE inventory_db OWNER inventory_user;

-- Pricing DB
CREATE USER pricing_user WITH PASSWORD 'pricing_pass';
CREATE DATABASE pricing_db OWNER pricing_user;

-- Order DB
CREATE USER order_user WITH PASSWORD 'order_pass';
CREATE DATABASE order_db OWNER order_user;
