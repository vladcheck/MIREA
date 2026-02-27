SELECT generate_order_numbers_valekzhanin(3) AS result; -- вернет 3 номера заказа
SELECT generate_order_numbers_valekzhanin(0) AS result; -- NULL
SELECT generate_order_numbers_valekzhanin(-3) AS result; -- NULL
SELECT generate_order_numbers_valekzhanin(NULL) AS result; -- NULL