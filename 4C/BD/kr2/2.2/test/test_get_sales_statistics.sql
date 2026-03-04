-- Статистика за 2025 год
SELECT * FROM get_sales_statistics_valekzhanin(2023); -- таблица результатов

-- Статистика за год без продаж
SELECT * FROM get_sales_statistics_valekzhanin(2020); -- пустая таблица

-- NULL в параметре года
SELECT * FROM get_sales_statistics_valekzhanin(NULL) AS result; -- RAISE