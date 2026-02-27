-- Успешный перевод
SELECT transfer_money_valekzhanin(1, 2, 100) AS result; -- t

-- NULL в первом параметре
SELECT transfer_money_valekzhanin(NULL, 2, 100) AS result; -- f

-- NULL во втором параметре
SELECT transfer_money_valekzhanin(1, NULL, 100) AS result; -- f

-- NULL в третьем параметре
SELECT transfer_money_valekzhanin(1, 2, NULL) AS result; -- f

-- Перевод превышает баланс
SELECT transfer_money_valekzhanin(1, 2, 10000) AS result; -- f

-- Перевод на несуществующий счет
SELECT transfer_money_valekzhanin(1, 99999, 100) AS result; -- f

-- Отрицательная сумма перевода
SELECT transfer_money_valekzhanin(1, 2, -100) AS result; -- f