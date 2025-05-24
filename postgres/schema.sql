-- postgres/schema.sql

CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID,
    product_id INT,
    quantity INT,
    price FLOAT,
    timestamp TIMESTAMP
);

CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    location VARCHAR(100),
    signup_date TIMESTAMP
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(100),
    price FLOAT,
    stock_level INT
);

-- CREATE TABLE order_items (
--     order_item_id UUID PRIMARY KEY,
--     order_id UUID REFERENCES orders(order_id),
--     product_id INT REFERENCES products(product_id),
--     quantity INT,
--     price FLOAT
-- );
-- CREATE TABLE inventory (
--     product_id INT PRIMARY KEY REFERENCES products(product_id),
--     stock_level INT,
--     last_updated TIMESTAMP
-- );
-- CREATE TABLE suppliers (
--     supplier_id UUID PRIMARY KEY,
--     name VARCHAR(100),
--     contact_info VARCHAR(100),
--     location VARCHAR(100)
-- );
-- CREATE TABLE supplier_products (
--     supplier_product_id UUID PRIMARY KEY,
--     supplier_id UUID REFERENCES suppliers(supplier_id),
--     product_id INT REFERENCES products(product_id),
--     supply_price FLOAT,
--     supply_date TIMESTAMP
-- );
-- CREATE TABLE shipments (
--     shipment_id UUID PRIMARY KEY,
--     order_id UUID REFERENCES orders(order_id),
--     shipment_date TIMESTAMP,
--     delivery_date TIMESTAMP,
--     status VARCHAR(50)
-- );
-- CREATE TABLE reviews (
--     review_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     customer_id UUID REFERENCES customers(customer_id),
--     rating INT CHECK (rating >= 1 AND rating <= 5),
--     comment TEXT,
--     review_date TIMESTAMP
-- );
-- CREATE TABLE discounts (
--     discount_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     discount_percentage FLOAT CHECK (discount_percentage >= 0 AND discount_percentage <= 100),
--     start_date TIMESTAMP,
--     end_date TIMESTAMP
-- );
-- CREATE TABLE payment_methods (
--     payment_method_id UUID PRIMARY KEY,
--     customer_id UUID REFERENCES customers(customer_id),
--     method_type VARCHAR(50),
--     details TEXT,
--     added_date TIMESTAMP
-- );
-- CREATE TABLE transactions (
--     transaction_id UUID PRIMARY KEY,
--     order_id UUID REFERENCES orders(order_id),
--     payment_method_id UUID REFERENCES payment_methods(payment_method_id),
--     amount FLOAT,
--     transaction_date TIMESTAMP,
--     status VARCHAR(50)
-- );
-- CREATE TABLE wishlists (
--     wishlist_id UUID PRIMARY KEY,
--     customer_id UUID REFERENCES customers(customer_id),
--     created_date TIMESTAMP
-- );
-- CREATE TABLE wishlist_items (
--     wishlist_item_id UUID PRIMARY KEY,
--     wishlist_id UUID REFERENCES wishlists(wishlist_id),
--     product_id INT REFERENCES products(product_id),
--     added_date TIMESTAMP
-- );
-- CREATE TABLE carts (
--     cart_id UUID PRIMARY KEY,
--     customer_id UUID REFERENCES customers(customer_id),
--     created_date TIMESTAMP
-- );
-- CREATE TABLE cart_items (
--     cart_item_id UUID PRIMARY KEY,
--     cart_id UUID REFERENCES carts(cart_id),
--     product_id INT REFERENCES products(product_id),
--     quantity INT,
--     added_date TIMESTAMP
-- );
-- CREATE TABLE product_images (
--     image_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     image_url VARCHAR(255),
--     alt_text VARCHAR(100),
--     uploaded_date TIMESTAMP
-- );
-- CREATE TABLE product_tags (
--     tag_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     tag_name VARCHAR(50),
--     created_date TIMESTAMP
-- );
-- CREATE TABLE product_attributes (
--     attribute_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     attribute_name VARCHAR(100),
--     attribute_value VARCHAR(100),
--     created_date TIMESTAMP
-- );
-- CREATE TABLE product_variants (
--     variant_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     variant_name VARCHAR(100),
--     additional_price FLOAT,
--     created_date TIMESTAMP
-- );
-- CREATE TABLE product_variant_attributes (
--     variant_attribute_id UUID PRIMARY KEY,
--     variant_id UUID REFERENCES product_variants(variant_id),
--     attribute_name VARCHAR(100),
--     attribute_value VARCHAR(100),
--     created_date TIMESTAMP
-- );
-- CREATE TABLE product_reviews (
--     product_review_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     customer_id UUID REFERENCES customers(customer_id),
--     rating INT CHECK (rating >= 1 AND rating <= 5),
--     comment TEXT,
--     review_date TIMESTAMP
-- );
-- CREATE TABLE product_categories (
--     category_id UUID PRIMARY KEY,
--     category_name VARCHAR(100),
--     parent_category_id UUID REFERENCES product_categories(category_id),
--     created_date TIMESTAMP
-- );
-- CREATE TABLE product_category_assignments (
--     assignment_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     category_id UUID REFERENCES product_categories(category_id),
--     assigned_date TIMESTAMP
-- );
-- CREATE TABLE product_price_history (
--     price_history_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     old_price FLOAT,
--     new_price FLOAT,
--     change_date TIMESTAMP
-- );
-- CREATE TABLE product_stock_history (
--     stock_history_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     old_stock_level INT,
--     new_stock_level INT,
--     change_date TIMESTAMP
-- );
-- CREATE TABLE product_sales (
--     sale_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     quantity_sold INT,
--     sale_date TIMESTAMP,
--     revenue FLOAT
-- );
-- CREATE TABLE product_views (
--     view_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     customer_id UUID REFERENCES customers(customer_id),
--     view_date TIMESTAMP
-- );
-- CREATE TABLE product_favorites (
--     favorite_id UUID PRIMARY KEY,
--     product_id INT REFERENCES products(product_id),
--     customer_id UUID REFERENCES customers(customer_id),
--     added_date TIMESTAMP
-- );
-- CREATE TABLE product_comparisons (
--     comparison_id UUID PRIMARY KEY,
--     customer_id UUID REFERENCES customers(customer_id),
--     created_date TIMESTAMP
-- );
-- CREATE TABLE product_comparison_items (
--     comparison_item_id UUID PRIMARY KEY,
--     comparison_id UUID REFERENCES product_comparisons(comparison_id),
--     product_id INT REFERENCES products(product_id),
--     added_date TIMESTAMP
-- );
-- CREATE TABLE product_bundles (
--     bundle_id UUID PRIMARY KEY,
--     bundle_name VARCHAR(100),
--     created_date TIMESTAMP
-- );

