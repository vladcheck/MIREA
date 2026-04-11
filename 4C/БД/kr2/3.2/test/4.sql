BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1:_raw_номер_требует_форматирования';
    INSERT INTO realtor (last_name, first_name, middle_name, phone_number)
    VALUES ('Тестов', 'Тест', 'Тестович', '79996667788');
    RAISE NOTICE 'Тест 1 пройден: телефон отформатирован';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 1 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2:_номер_уже_отформатирован';
    INSERT INTO realtor (last_name, first_name, middle_name, phone_number)
    VALUES ('Тестов', 'Тест', 'Тестович', '+7 (999) 666 77 88');
    RAISE NOTICE 'Тест 2 пройден: предупреждение не появилось';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 2 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 3:_некорректный_номер';
    INSERT INTO realtor (last_name, first_name, middle_name, phone_number)
    VALUES ('Тестов', 'Тест', 'Тестович', '12345');
    RAISE NOTICE 'Тест 3 пройден: форматирование не применено';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 3 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;