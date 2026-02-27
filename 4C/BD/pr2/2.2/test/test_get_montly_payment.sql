-- Расчет ипотеки (ставка 10%, срок 20 лет, взнос 1000000)
SELECT calculate_mortgage_payment_valekzhanin(1, 10.00, 20, 1000000) AS result; -- 48277.00

-- Расчет с большим взносом
SELECT calculate_mortgage_payment_valekzhanin(1, 10.00, 20, 3000000) AS result; -- 28966.00

-- NULL в параметре объекта
SELECT calculate_mortgage_payment_valekzhanin(NULL, 10.00, 20, 1000000) AS result; -- NULL

-- NULL в параметре ставки
SELECT calculate_mortgage_payment_valekzhanin(1, NULL, 20, 1000000) AS result; -- NULL

-- Взнос превышает стоимость
SELECT calculate_mortgage_payment_valekzhanin(1, 10.00, 20, 10000000) AS result; -- ОШИБКА