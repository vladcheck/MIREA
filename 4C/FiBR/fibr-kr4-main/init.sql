CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    age INTEGER,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

INSERT INTO users (first_name, last_name, age, created_at, updated_at) VALUES
('John', 'Doe', 30, NOW(), NOW()),
('Jane', 'Smith', 25, NOW(), NOW()),
('Bob', 'Johnson', 35, NOW(), NOW());

INSERT INTO products (name, description, price, stock, created_at, updated_at) VALUES
('Laptop', 'High-performance laptop', 999.99, 50, NOW(), NOW()),
('Smartphone', 'Latest smartphone model', 699.99, 100, NOW(), NOW()),
('Headphones', 'Wireless noise-canceling headphones', 199.99, 75, NOW(), NOW());
