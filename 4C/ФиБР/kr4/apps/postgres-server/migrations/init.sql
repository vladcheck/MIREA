CREATE DATABASE mydatabase;

DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    age INTEGER NOT NULL
);


DROP INDEX idx_user_id;
CREATE INDEX idx_user_id ON users (id);

DROP INDEX idx_user_full_name;
CREATE INDEX idx_user_full_name ON users (first_name, last_name);

DROP INDEX idx_user_age;
CREATE INDEX idx_user_age ON users (age);