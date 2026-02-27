SELECT categorize_order_valekzhanin(-100.00) AS result; -- ОТРИЦАТЕЛЬНОЕ ЧИСЛО
SELECT categorize_order_valekzhanin(500.00) AS result; -- МАЛЫЙ
SELECT categorize_order_valekzhanin(3000.00) AS result; -- СРЕДНИЙ
SELECT categorize_order_valekzhanin(10000.00) AS result; -- КРУПНЫЙ
SELECT categorize_order_valekzhanin(25000.00) AS result; -- ОСОБО КРУПНЫЙ
SELECT categorize_order_valekzhanin(NULL) AS result; -- NULL