CREATE OR REPLACE FUNCTION prevent_duplicate_sale_valekzhanin()
RETURNS TRIGGER AS $$
DECLARE
    v_existing_sale RECORD;
BEGIN
    SELECT * INTO v_existing_sale
    FROM sale
    WHERE property_id = NEW.property_id;

    IF FOUND THEN
        RAISE EXCEPTION 'Объект недвижимости с ID % уже был продан. Повторная продажа запрещена.',
            NEW.property_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_duplicate_sale_valekzhanin ON sale;

CREATE TRIGGER trg_prevent_duplicate_sale_valekzhanin
BEFORE INSERT ON sale
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_sale_valekzhanin();