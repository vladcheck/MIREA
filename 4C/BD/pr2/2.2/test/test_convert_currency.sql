-- Успешная конвертация (курс 90 рублей за доллар)
SELECT convert_currency_valekzhanin(90.00, 1) AS result; -- 55555.56

-- Конвертация по другому курсу
SELECT convert_currency_valekzhanin(100.00, 1) AS result; -- 50000.00

-- NULL в параметре курса
SELECT convert_currency_valekzhanin(NULL, 1) AS result; -- NULL

-- NULL в параметре объекта
SELECT convert_currency_valekzhanin(90.00, NULL) AS result; -- NULL

-- Несуществующий объект
SELECT convert_currency_valekzhanin(90.00, 99999) AS result; -- ОШИБКА