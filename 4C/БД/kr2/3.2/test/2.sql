BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1: Бонус в пределах нормы';
    UPDATE bonus SET amount = 100000 WHERE realtor_id = 1;
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Ошибка в тесте 1: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2: Превышение лимита бонуса';
    UPDATE bonus SET amount = 600000 WHERE realtor_id = 2;
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Ошибка в тесте 2: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 3: Превышение лимита при обновлении бонуса';
    UPDATE bonus SET amount = 600000 WHERE realtor_id = 3;
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Ошибка в тесте 3: %', SQLERRM;
END $$;
ROLLBACK;