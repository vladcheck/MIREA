CREATE OR REPLACE FUNCTION format_phone_valekzhanin()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.phone_number ~ '^\d{11}$' THEN
        NEW.phone_number := regexp_replace(NEW.phone_number, '(\d)(\d{3})(\d{3})(\d{2})(\d{2})', '+\1 (\2) \3 \4 \5');
        RAISE NOTICE 'Телефон риэлтора отформатирован: %', NEW.phone_number;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_format_phone_valekzhanin ON realtor;

CREATE TRIGGER trg_format_phone_valekzhanin
BEFORE INSERT OR UPDATE ON realtor
FOR EACH ROW
EXECUTE FUNCTION format_phone_valekzhanin();