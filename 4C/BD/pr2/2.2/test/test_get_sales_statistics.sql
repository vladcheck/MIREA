-- Статистика за 2025 год
SELECT * FROM sales_statistics_valekzhanin(2025); -- таблица результатов

-- Статистика за 2024 год
SELECT * FROM sales_statistics_valekzhanin(2024); -- таблица результатов

-- Статистика за год без продаж
SELECT * FROM sales_statistics_valekzhanin(2020); -- пустая таблица

-- NULL в параметре года
SELECT * FROM sales_statistics_valekzhanin(NULL) AS result; -- NULL