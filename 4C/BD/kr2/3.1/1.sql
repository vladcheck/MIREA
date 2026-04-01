CREATE OR REPLACE FUNCTION check_price_difference_valekzhanin()
RETURNS TRIGGER AS $$
DECLARE
    v_listed_price NUMERIC;
    v_sale_price NUMERIC;
    v_difference_percent NUMERIC;
    v_threshold_percent CONSTANT NUMERIC := 20.0;
BEGIN
    SELECT price INTO v_listed_price
    FROM property
    WHERE id = NEW.property_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Объект недвижимости с ID % не найден', NEW.property_id;
    END IF;

    IF v_listed_price IS NULL OR NEW.price IS NULL THEN
        RAISE EXCEPTION 'Цена не может быть NULL';
    END IF;

    IF v_listed_price <= 0 OR NEW.price <= 0 THEN
        RAISE EXCEPTION 'Цена должна быть положительным числом';
    END IF;

    v_sale_price := NEW.price;
    v_difference_percent := ABS((v_sale_price - v_listed_price) / v_listed_price * 100);

    IF v_difference_percent > v_threshold_percent THEN
        RAISE WARNING 'ВНИМАНИЕ: Разница между заявленной (%) и продажной (%) стоимостью составляет % (порог: % )',
            TO_CHAR(v_listed_price, 'FM999999990.00'),
            TO_CHAR(v_sale_price, 'FM999999990.00'),
            TO_CHAR(v_difference_percent, 'FM999999990.00'),
            TO_CHAR(v_threshold_percent, 'FM999999990.0');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_price_difference_valekzhanin ON sale;

CREATE TRIGGER trg_check_price_difference_valekzhanin
BEFORE INSERT OR UPDATE ON sale
FOR EACH ROW
EXECUTE FUNCTION check_price_difference_valekzhanin();