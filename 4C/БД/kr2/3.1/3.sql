CREATE OR REPLACE FUNCTION check_structure_area_valekzhanin()
RETURNS TRIGGER AS $$
DECLARE
    v_property_area NUMERIC;
    v_current_sum NUMERIC;
    v_total_sum NUMERIC;
    v_excess NUMERIC;
BEGIN
    SELECT area INTO v_property_area
    FROM property
    WHERE id = NEW.property_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Объект недвижимости с ID % не найден', NEW.property_id;
    END IF;

    SELECT COALESCE(SUM(room_area), 0) INTO v_current_sum
    FROM property_structure
    WHERE property_id = NEW.property_id;

    v_total_sum := v_current_sum + NEW.room_area;

    IF v_total_sum > v_property_area THEN
        v_excess := v_total_sum - v_property_area;
        RAISE NOTICE 'ВНИМАНИЕ: Превышение площади составляет % кв.м. (Сумма: %, Лимит: %)',
            TO_CHAR(v_excess, 'FM999999990.00'),
            TO_CHAR(v_total_sum, 'FM999999990.00'),
            TO_CHAR(v_property_area, 'FM999999990.00');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_structure_area_valekzhanin ON property_structure;

CREATE TRIGGER trg_check_structure_area_valekzhanin
BEFORE INSERT ON property_structure
FOR EACH ROW
EXECUTE FUNCTION check_structure_area_valekzhanin();