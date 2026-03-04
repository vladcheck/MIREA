CREATE OR REPLACE FUNCTION generate_order_numbers_valekzhanin(count INTEGER)
RETURNS TABLE(order_number TEXT)
RETURNS NULL ON NULL INPUT
AS $$
    SELECT 'ORD-' || TO_CHAR(NOW(), 'YYYYMM') || LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0')
    FROM generate_series(1, count);
$$ LANGUAGE SQL;