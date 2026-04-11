CREATE OR REPLACE FUNCTION update_realtor_bonus_valekzhanin()
RETURNS TRIGGER AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT EXISTS(SELECT 1 FROM bonus WHERE realtor_id = NEW.realtor_id) INTO v_exists;
        IF v_exists THEN
            UPDATE bonus SET amount = amount + NEW.price * 0.05 WHERE realtor_id = NEW.realtor_id;
            RAISE NOTICE 'Бонус обновлен для риэлтора %', NEW.realtor_id;
        ELSE
            INSERT INTO bonus (realtor_id, amount) VALUES (NEW.realtor_id, NEW.price * 0.05);
            RAISE NOTICE 'Запись бонуса создана для риэлтора %', NEW.realtor_id;
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE bonus SET amount = amount - OLD.price * 0.05 WHERE realtor_id = OLD.realtor_id;
        RAISE NOTICE 'Бонус уменьшен для риэлтора %', OLD.realtor_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_realtor_bonus_valekzhanin ON sale;
CREATE TRIGGER trg_update_realtor_bonus_valekzhanin
AFTER INSERT OR DELETE ON sale
FOR EACH ROW EXECUTE FUNCTION update_realtor_bonus_valekzhanin();