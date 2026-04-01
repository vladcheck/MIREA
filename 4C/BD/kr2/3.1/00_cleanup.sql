DO $$
BEGIN
    DROP TRIGGER IF EXISTS trg_update_realtor_bonus_valekzhanin ON sale;
    DROP TRIGGER IF EXISTS trg_check_bonus_limit_valekzhanin ON bonus;
    DROP TRIGGER IF EXISTS trg_check_passport_format_valekzhanin ON realtor;
    DROP TRIGGER IF EXISTS trg_format_phone_valekzhanin ON realtor;

    DROP TABLE IF EXISTS bonus CASCADE;

    ALTER TABLE realtor DROP COLUMN IF EXISTS passport_data;
END $$;