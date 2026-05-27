SET client_min_messages TO NOTICE;

TRUNCATE trips_archive, trip_sales, trips, routes, buses, drivers RESTART IDENTITY CASCADE;

INSERT INTO drivers (full_name) VALUES ('Иванов Иван Сергеевич'), ('Петров Петр Петрович');
INSERT INTO buses (plate_number, capacity) VALUES ('А111АА', 40), ('Б222ББ', 20);
INSERT INTO routes (route_name, start_point, end_point, distance_km) VALUES ('Москва-Тверь', 'Москва', 'Тверь', 160.5);

DO $$
DECLARE v_res TIMESTAMP; v_exp TIMESTAMP := '2024-05-10 10:30:00';
BEGIN
    RAISE NOTICE '[Тест 1.1] calc_arrival_time_valekzhanin';
    RAISE NOTICE 'Вход: 2024-05-10 08:00:00 + 02:30:00';
    v_res := calc_arrival_time_valekzhanin('2024-05-10 08:00:00', '02:30:00');
    RAISE NOTICE 'Ожидалось: %, Получено: %', v_exp, v_res;
    RAISE NOTICE 'Итог: %', CASE WHEN v_res = v_exp THEN 'УСПЕХ' ELSE 'НЕ ПРОЙДЕНО' END;
    RAISE NOTICE '---';
END $$;

DO $$
DECLARE v_res INT; v_exp INT := 1;
BEGIN
    RAISE NOTICE '[Тест 1.2] is_trip_today_valekzhanin (ежедн.)';
    v_res := is_trip_today_valekzhanin('ежедн.');
    RAISE NOTICE 'Ожидалось: %, Получено: %', v_exp, v_res;
    RAISE NOTICE 'Итог: %', CASE WHEN v_res = v_exp THEN 'УСПЕХ' ELSE 'НЕ ПРОЙДЕНО' END;
    RAISE NOTICE '---';
END $$;

DO $$
DECLARE v_res VARCHAR; v_exp VARCHAR := 'Иванов И.С.';
BEGIN
    RAISE NOTICE '[Тест 1.3] format_fio_valekzhanin';
    RAISE NOTICE 'Вход: Иванов Иван Сергеевич';
    v_res := format_fio_valekzhanin('Иванов Иван Сергеевич');
    RAISE NOTICE 'Ожидалось: %, Получено: %', v_exp, v_res;
    RAISE NOTICE 'Итог: %', CASE WHEN v_res = v_exp THEN 'УСПЕХ' ELSE 'НЕ ПРОЙДЕНО' END;
    RAISE NOTICE '---';
END $$;

DO $$
BEGIN
    RAISE NOTICE '[Тест 2.1] Trigger trg_check_tickets (valid insert)';
    INSERT INTO trips (driver_id, bus_id, route_id, departure_time, travel_duration, cost, frequency)
    VALUES (1, 1, 1, NOW(), '01:00:00', 500, 'ежедн.');
    INSERT INTO trip_sales (trip_id, sold_count) VALUES (1, 10);
    RAISE NOTICE 'Вход: sold_count=10, bus_capacity=40';
    RAISE NOTICE 'Ожидалось: Успешный INSERT';
    RAISE NOTICE 'Итог: УСПЕХ';
    RAISE NOTICE '---';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Итог: НЕ ПРОЙДЕНО (%)', SQLERRM;
    RAISE NOTICE '---';
END $$;

DO $$
BEGIN
    RAISE NOTICE '[Тест 2.2] Trigger trg_check_tickets (invalid insert)';
    INSERT INTO trip_sales (trip_id, sold_count) VALUES (1, 45);
    RAISE NOTICE 'Итог: НЕ ПРОЙДЕНО (триггер должен был заблокировать INSERT)';
    RAISE NOTICE '---';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Вход: sold_count=45, bus_capacity=40';
    RAISE NOTICE 'Ожидалось: Исключение';
    RAISE NOTICE 'Получено: %', SQLERRM;
    RAISE NOTICE 'Итог: УСПЕХ';
    RAISE NOTICE '---';
END $$;

DO $$
BEGIN
    RAISE NOTICE '[Тест 2.3] Trigger trg_validate_route (empty name)';
    INSERT INTO routes (route_name, start_point, end_point, distance_km) VALUES ('', 'А', 'Б', 10);
    RAISE NOTICE 'Итог: НЕ ПРОЙДЕНО';
    RAISE NOTICE '---';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Вход: route_name=''';
    RAISE NOTICE 'Ожидалось: Исключение';
    RAISE NOTICE 'Получено: %', SQLERRM;
    RAISE NOTICE 'Итог: УСПЕХ';
    RAISE NOTICE '---';
END $$;

DO $$
DECLARE v_cnt INT;
BEGIN
    RAISE NOTICE '[Тест 2.4] Trigger trg_archive_trip (delete trip)';
    DELETE FROM trips WHERE id = 1;
    SELECT COUNT(*) INTO v_cnt FROM trips_archive;
    RAISE NOTICE 'Вход: Delete trip id=1';
    RAISE NOTICE 'Ожидалось: 1 row in archive table';
    RAISE NOTICE 'Получено: % строк', v_cnt;
    RAISE NOTICE 'Итог: %', CASE WHEN v_cnt = 1 THEN 'УСПЕХ' ELSE 'НЕ ПРОЙДЕНО' END;
    RAISE NOTICE '---';
END $$;

DO $$
BEGIN
    RAISE NOTICE '[Тест 3.1] Процедура get_driver_schedule_valekzhanin';
    RAISE NOTICE 'Вход: driver_id=1, current month';
    CALL get_driver_schedule_valekzhanin(1);
    RAISE NOTICE 'Итог: УСПЕХ (ошибок нет)';
    RAISE NOTICE '---';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Итог: НЕ ПРОЙДЕНО (%)', SQLERRM;
    RAISE NOTICE '---';
END $$;

DO $$
BEGIN
    INSERT INTO trips (driver_id, bus_id, route_id, departure_time, travel_duration, cost, frequency) VALUES
    (1, 1, 1, CURRENT_DATE + INTERVAL '09:00', '02:00', 300, 'ежедн.'),
    (1, 1, 1, CURRENT_DATE + INTERVAL '10:30', '02:00', 400, 'ежедн.'),
    (1, 1, 1, CURRENT_DATE + INTERVAL '13:00', '02:00', 200, 'ежедн.'),
    (1, 1, 1, CURRENT_DATE + INTERVAL '16:00', '01:30', 250, 'ежедн.');

    RAISE NOTICE '[Тест 3.2] Процедура check_driver_violations_valekzhanin';
    RAISE NOTICE 'Вход: 4 trips/day, total >6h, gaps <1h, mismatched endpoints';
    CALL check_driver_violations_valekzhanin();
    RAISE NOTICE 'Итог: УСПЕХ (ошибок нет)';
    RAISE NOTICE '---';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Итог: НЕ ПРОЙДЕНО (%)', SQLERRM;
    RAISE NOTICE '---';
END $$;

DO $$
DECLARE v_cost NUMERIC; v_exp NUMERIC := 1150.00;
BEGIN
    RAISE NOTICE '[Тест 3.3] Процедура calc_month_cost_valekzhanin';
    RAISE NOTICE 'Вход: driver_id=1, date=CURRENT_DATE';
    CALL calc_month_cost_valekzhanin(1, CURRENT_DATE, v_cost);
    RAISE NOTICE 'Ожидалось: %, Получено: %', v_exp, v_cost;
    RAISE NOTICE 'Итог: %', CASE WHEN v_cost = v_exp THEN 'УСПЕХ' ELSE 'НЕ ПРОЙДЕНО' END;
    RAISE NOTICE '---';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Итог: НЕ ПРОЙДЕНО (%)', SQLERRM;
    RAISE NOTICE '---';
END $$;

DO $$
BEGIN
RAISE NOTICE '=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===';
END $$;
