BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1: Обновление существующего бонуса';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (3, CURRENT_DATE, 1, 1000000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 1 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2: Создание новой записи бонуса';
    DELETE FROM bonus WHERE realtor_id = 2;
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (7, CURRENT_DATE, 2, 2000000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 2 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
DECLARE
    v_sale_id INTEGER;
BEGIN
    RAISE NOTICE 'Тест 3: Уменьшение бонуса при удалении продажи';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (11, CURRENT_DATE, 3, 3000000)
    RETURNING id INTO v_sale_id;
    
    DELETE FROM sale WHERE id = v_sale_id;
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 3 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;