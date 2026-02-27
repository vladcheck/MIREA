CREATE OR REPLACE FUNCTION categorize_order_valekzhanin(order_amount DECIMAL(10,2))
    RETURNS TEXT
    RETURNS NULL ON NULL INPUT
    AS $$
    BEGIN
        IF order_amount < 0 THEN
            RETURN 'ОТРИЦАТЕЛЬНОЕ ЧИСЛО';
        ELSIF order_amount < 1000 THEN
            RETURN 'МАЛЫЙ';
        ELSIF order_amount < 5000 THEN
            RETURN 'СРЕДНИЙ';
        ELSIF order_amount < 20000 THEN
            RETURN 'КРУПНЫЙ';
        ELSE
            RETURN 'ОСОБО КРУПНЫЙ';
        END IF;
    END;
    $$ LANGUAGE plpgsql;