CREATE OR REPLACE FUNCTION categorize_order_valekzhanin(order_amount DECIMAL(10,2))
RETURNS TEXT
RETURNS NULL ON NULL INPUT
AS $$
    SELECT CASE
        WHEN order_amount < 0 THEN 'ОТРИЦАТЕЛЬНОЕ ЧИСЛО'
        WHEN order_amount < 1000 THEN 'МАЛЫЙ'
        WHEN order_amount < 5000 THEN 'СРЕДНИЙ'
        WHEN order_amount < 20000 THEN 'КРУПНЫЙ'
        ELSE 'ОСОБО КРУПНЫЙ'
    END;
$$ LANGUAGE SQL;