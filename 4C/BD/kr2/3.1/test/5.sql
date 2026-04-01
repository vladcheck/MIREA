ALTER TABLE sale DISABLE TRIGGER trg_prevent_duplicate_sale_valekzhanin;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1: Проверка INSERT';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (26, CURRENT_DATE, 1, 1000000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 1 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2: Проверка UPDATE';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (28, CURRENT_DATE, 1, 2000000);
    UPDATE sale SET price = 2500000
    WHERE property_id = 28 AND realtor_id = 1;
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
    RAISE NOTICE 'Тест 3: Проверка DELETE';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (30, CURRENT_DATE, 1, 3000000)
    RETURNING id INTO v_sale_id;
    DELETE FROM sale WHERE id = v_sale_id;
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 3 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

ALTER TABLE sale ENABLE TRIGGER trg_prevent_duplicate_sale_valekzhanin;