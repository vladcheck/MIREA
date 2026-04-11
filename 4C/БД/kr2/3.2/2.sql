CREATE OR REPLACE FUNCTION check_bonus_limit_valekzhanin()
RETURNS TRIGGER AS $$
DECLARE
    v_max_bonus CONSTANT NUMERIC := 500000;
    v_current_bonus NUMERIC;
BEGIN
    SELECT COALESCE(amount, 0) INTO v_current_bonus
    FROM bonus
    WHERE realtor_id = NEW.realtor_id;

    IF TG_OP = 'INSERT' THEN
        v_current_bonus := v_current_bonus + NEW.amount;
    ELSIF TG_OP = 'UPDATE' THEN
        v_current_bonus := NEW.amount;
    END IF;

    IF v_current_bonus > v_max_bonus THEN
        RAISE NOTICE 'ВНИМАНИЕ: Накопленный бонус риэлтора % (%) превысил лимит (%)',
            NEW.realtor_id,
            TO_CHAR(v_current_bonus, 'FM999999999.00'),
            TO_CHAR(v_max_bonus, 'FM999999999.00');
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_bonus_limit_valekzhanin ON bonus;

CREATE TRIGGER trg_check_bonus_limit_valekzhanin
AFTER INSERT OR UPDATE ON bonus
FOR EACH ROW
EXECUTE FUNCTION check_bonus_limit_valekzhanin();