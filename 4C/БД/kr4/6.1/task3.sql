DROP VIEW v_current_trips_valekzhanin;
CREATE VIEW v_current_trips_valekzhanin AS
SELECT 
    t.id,
    t.departure_point,
    t.arrival_point,
    t.departure_time,
    t.arrival_time,
    t.distance,
    t.sold_ticket_count
FROM Trip t
WHERE NOW() BETWEEN t.departure_time AND t.arrival_time;

DROP VIEW v_schedule_today_valekzhanin;
CREATE VIEW v_schedule_today_valekzhanin AS
SELECT 
    id,
    departure_point,
    arrival_point,
    departure_time,
    arrival_time,
    LEAD(departure_time) OVER (PARTITION BY driver_id ORDER BY departure_time) - arrival_time AS break_until_next
FROM Trip
WHERE departure_time::date = CURRENT_DATE;

DROP VIEW v_trip_cost_valekzhanin;
CREATE VIEW v_trip_cost_valekzhanin AS
SELECT 
    t.id AS trip_id,
    ct.base_price * v.base_price_coefficient * t.distance AS cost
FROM Trip t
JOIN Driver d ON t.driver_id = d.id
JOIN Vehicle v ON d.vehicle_license_plate = v.license_plate
JOIN CarType ct ON v.type = ct.class;
