CREATE OR REPLACE FUNCTION check_sale_date_valekzhanin()
RETURNS TRIGGER AS $$
DECLARE
    v_listing_date DATE;
BEGIN
    SELECT listing_date INTO v_listing_date
    FROM property
    WHERE id = NEW.property_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Объект недвижимости с ID % не найден', NEW.property_id;
    END IF;

    IF NEW.sale_date < v_listing_date THEN
        RAISE NOTICE 'ВНИМАНИЕ: Дата продажи (%) раньше даты размещения объявления (%)',
            NEW.sale_date, v_listing_date;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_sale_date_valekzhanin ON sale;

CREATE TRIGGER trg_check_sale_date_valekzhanin
BEFORE INSERT OR UPDATE ON sale
FOR EACH ROW
EXECUTE FUNCTION check_sale_date_valekzhanin();