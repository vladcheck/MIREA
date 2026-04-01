ALTER TABLE sale DISABLE TRIGGER trg_prevent_duplicate_sale_valekzhanin;
BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1: Дата продажи корректна';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (21, '2025-09-01', 1, 5000000);
    RAISE NOTICE 'Тест 1 пройден: предупреждение НЕ появилось';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 1 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;
BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2: Дата продажи раньше размещения';
    INSERT INTO sale (property_id, sale_date, realtor_id, price)
    VALUES (23, '2022-01-01', 1, 5000000);
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 2 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;
ALTER TABLE sale ENABLE TRIGGER trg_prevent_duplicate_sale_valekzhanin;