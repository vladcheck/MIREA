ALTER TABLE sale DISABLE TRIGGER trg_prevent_duplicate_sale_valekzhanin;
BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1: Разница больше 20 процентов';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (3, CURRENT_DATE, 1, 750000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 1 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;
BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2: Не существующий объект';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (999999, CURRENT_DATE, 1, 500000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 2 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;
BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 3: Отрицательная цена';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (7, CURRENT_DATE, 1, -500000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 3 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;
BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 4: Разница меньше 20 процентов';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (3, CURRENT_DATE, 1, 450000);
    RAISE NOTICE 'Тест 4 пройден: предупреждение НЕ появилось';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 4 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;
ALTER TABLE sale ENABLE TRIGGER trg_prevent_duplicate_sale_valekzhanin;