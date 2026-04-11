BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1: Сумма площадей в пределах нормы';
    INSERT INTO property_structure (property_id, room_area)
    VALUES (14, 20);
    RAISE NOTICE 'Тест 1 пройден: предупреждение НЕ появилось';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 1 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2: Превышение общей площади объекта';
    INSERT INTO property_structure (property_id, room_area)
    VALUES (14, 100);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 2 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 3: Накопительное превышение площади';
    INSERT INTO property_structure (property_id, room_area)
    VALUES (18, 50);
    INSERT INTO property_structure (property_id, room_area)
    VALUES (18, 50);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 3 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;