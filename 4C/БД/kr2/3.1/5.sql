CREATE OR REPLACE FUNCTION log_sale_action_valekzhanin()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO journal (datetime, action, user_name)
    VALUES (CURRENT_TIMESTAMP, TG_OP, current_user);

    IF TG_OP = 'INSERT' THEN
        RAISE NOTICE 'Journal: INSERT operation on sale';
    ELSIF TG_OP = 'UPDATE' THEN
        RAISE NOTICE 'Journal: UPDATE operation on sale';
    ELSIF TG_OP = 'DELETE' THEN
        RAISE NOTICE 'Journal: DELETE operation on sale';
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_log_sale_action_valekzhanin ON sale;

CREATE TRIGGER trg_log_sale_action_valekzhanin
AFTER INSERT OR UPDATE OR DELETE ON sale
FOR EACH ROW
EXECUTE FUNCTION log_sale_action_valekzhanin();