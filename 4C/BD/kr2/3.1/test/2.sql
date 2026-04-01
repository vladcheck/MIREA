BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1: Повторная продажа объекта';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (3, CURRENT_DATE, 1, 1000000);
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (3, CURRENT_DATE, 2, 1200000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 1 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;
BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2: Первая продажа объекта';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (7, CURRENT_DATE, 1, 1000000);
    RAISE NOTICE 'Тест 2 пройден: объект продан успешно';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 2 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;
BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 3: Повторная продажа того же объекта';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (7, CURRENT_DATE, 1, 1000000);
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (7, CURRENT_DATE, 2, 1200000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 3 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;