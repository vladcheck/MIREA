-- Расчет зарплаты (коэффициент 0.01, премия 10000, февраль 2025)
SELECT get_realtor_salary_valekzhanin(0.01, 10000, 2, 2025, 'Иванов') AS result; -- 40000.00

-- Расчет без премии
SELECT get_realtor_salary_valekzhanin(0.01, 0, 2, 2025, 'Иванов') AS result; -- 30000.00

-- NULL в параметре коэффициента
SELECT get_realtor_salary_valekzhanin(NULL, 10000, 2, 2025, 'Иванов') AS result; -- NULL

-- NULL в параметре фамилии
SELECT get_realtor_salary_valekzhanin(0.01, 10000, 2, 2025, NULL) AS result; -- NULL

-- Несуществующий риэлтор
SELECT get_realtor_salary_valekzhanin(0.01, 10000, 2, 2025, 'Петров') AS result; -- ОШИБКА