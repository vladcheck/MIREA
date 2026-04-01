ALTER TABLE realtor ADD COLUMN IF NOT EXISTS passport_data VARCHAR(11);

CREATE OR REPLACE FUNCTION check_passport_format_valekzhanin()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.passport_data IS NOT NULL THEN
        IF NEW.passport_data !~ '^\d{4} \d{6}$' THEN
            RAISE EXCEPTION 'Некорректные паспортные данные. Ожидается формат: ХХХХ УУУУУУ (получено: %)', NEW.passport_data;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_passport_format_valekzhanin ON realtor;

CREATE TRIGGER trg_check_passport_format_valekzhanin
BEFORE INSERT OR UPDATE ON realtor
FOR EACH ROW
EXECUTE FUNCTION check_passport_format_valekzhanin();