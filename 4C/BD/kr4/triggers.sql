CREATE OR REPLACE FUNCTION fn_check_ticket_limit_valekzhanin()
RETURNS TRIGGER AS $$
DECLARE
    v_capacity INT;
BEGIN
    SELECT b.capacity INTO v_capacity
    FROM trips t
    JOIN buses b ON t.bus_id = b.id
    WHERE t.id = NEW.trip_id;

    IF NEW.sold_count > v_capacity THEN
        RAISE EXCEPTION 'Продано билетов больше, чем мест в автобусе (лимит: %)', v_capacity;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_tickets
BEFORE INSERT OR UPDATE ON trip_sales
FOR EACH ROW EXECUTE FUNCTION fn_check_ticket_limit_valekzhanin();

CREATE OR REPLACE FUNCTION fn_validate_route_valekzhanin()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.route_name IS NULL OR trim(NEW.route_name) = '' THEN
        RAISE EXCEPTION 'Название маршрута не может быть пустым';
    END IF;
    IF NEW.start_point IS NULL OR trim(NEW.start_point) = '' THEN
        RAISE EXCEPTION 'Начальный пункт не может быть пустым';
    END IF;
    IF NEW.end_point IS NULL OR trim(NEW.end_point) = '' THEN
        RAISE EXCEPTION 'Конечный пункт не может быть пустым';
    END IF;
    IF NEW.start_point = NEW.end_point THEN
        RAISE EXCEPTION 'Начальный и конечный пункты не могут совпадать';
    END IF;
    IF NEW.distance_km <= 0 THEN
        RAISE EXCEPTION 'Расстояние должно быть больше 0';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_route
BEFORE INSERT OR UPDATE ON routes
FOR EACH ROW EXECUTE FUNCTION fn_validate_route_valekzhanin();

CREATE OR REPLACE FUNCTION fn_archive_trip_valekzhanin()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO trips_archive (id, driver_id, bus_id, route_id, departure_time, travel_duration, cost, frequency)
    VALUES (OLD.id, OLD.driver_id, OLD.bus_id, OLD.route_id, OLD.departure_time, OLD.travel_duration, OLD.cost, OLD.frequency);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_archive_trip
AFTER DELETE ON trips
FOR EACH ROW EXECUTE FUNCTION fn_archive_trip_valekzhanin();
