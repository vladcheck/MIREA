CREATE OR REPLACE PROCEDURE get_driver_schedule_valekzhanin(p_driver_id INT)
LANGUAGE plpgsql AS $$
DECLARE
    r RECORD;
    v_start DATE;
    v_end DATE;
BEGIN
    v_start := DATE_TRUNC('month', CURRENT_DATE)::DATE;
    v_end := (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month - 1 day')::DATE;

    RAISE NOTICE 'Расписание водителя % за % - %:', p_driver_id, v_start, v_end;

    FOR r IN
        SELECT t.id, t.departure_time, t.travel_duration, rt.route_name, rt.start_point, rt.end_point
        FROM trips t
        JOIN routes rt ON t.route_id = rt.id
        WHERE t.driver_id = p_driver_id
          AND t.departure_time::DATE BETWEEN v_start AND v_end
        ORDER BY t.departure_time
    LOOP
        RAISE NOTICE 'Рейс %: Отправление %, Маршрут % - %', r.id, r.departure_time, r.route_name, r.start_point || ' -> ' || r.end_point;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE check_driver_violations_valekzhanin()
LANGUAGE plpgsql AS $$
DECLARE
    day_rec RECORD;
    trip_rec RECORD;
    prev_arr TIMESTAMP;
    prev_end TEXT;
BEGIN
    FOR day_rec IN
        SELECT driver_id, departure_time::DATE AS d_date,
               COUNT(*) AS cnt,
               SUM(travel_duration) AS total_dur
        FROM trips
        WHERE departure_time >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY driver_id, departure_time::DATE
    LOOP
        IF day_rec.cnt > 3 THEN
            RAISE NOTICE 'Водитель %: более 3 рейсов в день %', day_rec.driver_id, day_rec.d_date;
        END IF;
        IF day_rec.total_dur > INTERVAL '6 hours' THEN
            RAISE NOTICE 'Водитель %: время в пути > 6ч в день %', day_rec.driver_id, day_rec.d_date;
        END IF;

        prev_arr := NULL;
        prev_end := NULL;
        FOR trip_rec IN
            SELECT t.id, t.departure_time, t.travel_duration, r.start_point, r.end_point
            FROM trips t
            JOIN routes r ON t.route_id = r.id
            WHERE t.driver_id = day_rec.driver_id AND t.departure_time::DATE = day_rec.d_date
            ORDER BY t.departure_time
        LOOP
            IF prev_arr IS NOT NULL THEN
                IF trip_rec.departure_time - prev_arr < INTERVAL '1 hour' THEN
                    RAISE NOTICE 'Водитель %: промежуток < 1ч перед рейсом %', day_rec.driver_id, trip_rec.id;
                END IF;
                IF prev_end <> trip_rec.start_point THEN
                    RAISE NOTICE 'Водитель %: несоответствие пунктов перед рейсом %', day_rec.driver_id, trip_rec.id;
                END IF;
            END IF;
            prev_arr := trip_rec.departure_time + trip_rec.travel_duration;
            prev_end := trip_rec.end_point;
        END LOOP;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE calc_month_cost_valekzhanin(p_driver_id INT, p_date DATE, OUT p_total_cost NUMERIC)
LANGUAGE plpgsql AS $$
DECLARE
    v_year INT;
    v_month INT;
BEGIN
    v_year := EXTRACT(YEAR FROM p_date);
    v_month := EXTRACT(MONTH FROM p_date);

    SELECT COALESCE(SUM(t.cost), 0) INTO p_total_cost
    FROM trips t
    WHERE t.driver_id = p_driver_id
      AND EXTRACT(YEAR FROM t.departure_time + t.travel_duration) = v_year
      AND EXTRACT(MONTH FROM t.departure_time + t.travel_duration) = v_month;
      
    RAISE NOTICE 'Общая стоимость рейсов за месяц: %', p_total_cost;
END;
$$;
