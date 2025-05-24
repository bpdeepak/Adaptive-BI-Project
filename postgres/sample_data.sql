-- Insert sample customers
INSERT INTO customers (customer_id, name, email, location, signup_date) VALUES
('11111111-1111-1111-1111-111111111111', 'Alice Smith', 'alice@example.com', 'New York', NOW() - INTERVAL '1 year'),
('22222222-2222-2222-2222-222222222222', 'Bob Johnson', 'bob@example.com', 'Los Angeles', NOW() - INTERVAL '6 months'),
('33333333-3333-3333-3333-333333333333', 'Carol Davis', 'carol@example.com', 'Chicago', NOW() - INTERVAL '3 months');

-- Insert sample products
INSERT INTO products (product_id, name, category, price, stock_level) VALUES
(1, 'Laptop', 'Electronics', 1200, 50),
(2, 'Smartphone', 'Electronics', 800, 100),
(3, 'Headphones', 'Accessories', 150, 200),
(4, 'Camera', 'Electronics', 600, 30),
(5, 'Tablet', 'Electronics', 500, 70);
