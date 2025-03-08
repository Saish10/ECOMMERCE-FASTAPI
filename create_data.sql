-- Insert sample data into Customers
INSERT INTO Customers (first_name, last_name, email, phone, address, city, state, zip_code) VALUES
('John', 'Doe', 'john.doe@example.com', '123-456-7890', '123 Elm St', 'Los Angeles', 'CA', '90001'),
('Jane', 'Smith', 'jane.smith@example.com', '987-654-3210', '456 Maple Ave', 'San Francisco', 'CA', '94105'),
('Alice', 'Johnson', 'alice.johnson@example.com', '555-123-4567', '789 Oak Blvd', 'San Diego', 'CA', '92101');

-- Insert sample data into Products
INSERT INTO Products (product_name, description, category, price, stock_quantity) VALUES
('Laptop', '15-inch gaming laptop', 'Electronics', 1200.00, 10),
('Smartphone', 'Latest model with 5G', 'Electronics', 800.00, 20),
('Headphones', 'Noise-canceling wireless headphones', 'Accessories', 150.00, 50);