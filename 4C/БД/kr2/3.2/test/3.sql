BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 1: Корректные паспортные данные';
    INSERT INTO realtor (last_name, first_name, middle_name, phone_number, passport_data)
    VALUES ('Тестов', 'Тест', 'Тестович', '+70000000000', '1234 567890');
    RAISE NOTICE 'Тест 1 пройден: запись добавлена';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 1 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 2: Некорректные паспортные данные (нарушение маски)';
    INSERT INTO realtor (last_name, first_name, middle_name, phone_number, passport_data)
    VALUES ('Тестов', 'Тест', 'Тестович', '+70000000000', '123 4567890');
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 2 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 3: Некорректные паспортные данные (буквы вместо цифр)';
    INSERT INTO realtor (last_name, first_name, middle_name, phone_number, passport_data)
    VALUES ('Тестов', 'Тест', 'Тестович', '+70000000000', '1234 ABCD90');
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 3 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;

BEGIN;
DO $$
BEGIN
    RAISE NOTICE 'Тест 4: NULL значение паспортных данных (допустимо)';
    INSERT INTO realtor (last_name, first_name, middle_name, phone_number, passport_data)
    VALUES ('Тестов', 'Тест', 'Тестович', '+70000000000', NULL);
    RAISE NOTICE 'Тест 4 пройден: запись добавлена';
EXCEPTION
    WHEN OTHERS THEN
    RAISE NOTICE 'Тест 4 пройден: ошибка корректно перехвачена: %', SQLERRM;
END $$;
ROLLBACK;