DROP TABLE IF EXISTS trips_archive CASCADE;
DROP TABLE IF EXISTS trip_sales CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS buses CASCADE;
DROP TABLE IF EXISTS drivers CASCADE;

CREATE TABLE drivers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL
);

CREATE TABLE buses (
    id SERIAL PRIMARY KEY,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0)
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    route_name VARCHAR(50) NOT NULL,
    start_point VARCHAR(50) NOT NULL,
    end_point VARCHAR(50) NOT NULL,
    distance_km NUMERIC(5,2) NOT NULL CHECK (distance_km > 0)
);

CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    driver_id INT REFERENCES drivers(id) ON DELETE SET NULL,
    bus_id INT REFERENCES buses(id),
    route_id INT REFERENCES routes(id),
    departure_time TIMESTAMP NOT NULL,
    travel_duration INTERVAL NOT NULL,
    cost NUMERIC(10,2) NOT NULL CHECK (cost >= 0),
    frequency VARCHAR(10) CHECK (frequency IN ('daily', 'even', 'odd', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'ежедн.', 'четн.', 'нечет.', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс'))
);

CREATE TABLE trip_sales (
    trip_id INT PRIMARY KEY REFERENCES trips(id) ON DELETE CASCADE,
    sold_count INT NOT NULL DEFAULT 0 CHECK (sold_count >= 0)
);

CREATE TABLE trips_archive (
    id INT,
    driver_id INT,
    bus_id INT,
    route_id INT,
    departure_time TIMESTAMP,
    travel_duration INTERVAL,
    cost NUMERIC(10,2),
    frequency VARCHAR(10),
    deleted_at TIMESTAMP DEFAULT NOW()
);
