CREATE OR REPLACE FUNCTION transfer_money_valekzhanin(
    from_account_id INTEGER,
    to_account_id INTEGER,
    amount DECIMAL(10,2)
)
RETURNS BOOLEAN
AS $$
DECLARE
    sender_record accounts%ROWTYPE;
    receiver_record accounts%ROWTYPE;
BEGIN
    IF from_account_id IS NULL OR to_account_id IS NULL OR amount IS NULL THEN
        RETURN FALSE;
    END IF;

    IF amount <= 0 THEN
        RETURN FALSE;
    END IF;

    -- Проверка существования счетов и получение их данных
    SELECT * INTO sender_record FROM accounts WHERE id = from_account_id;
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SELECT * INTO receiver_record FROM accounts WHERE id = to_account_id;
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Проверка достаточности средств
    IF sender_record.balance < amount THEN
        RETURN FALSE;
    END IF;

    -- Выполнение перевода (списание и зачисление)
    UPDATE accounts SET balance = balance - amount WHERE id = from_account_id;
    UPDATE accounts SET balance = balance + amount WHERE id = to_account_id;

    -- Логирование транзакции
    INSERT INTO transactions (from_account, to_account, amount)
    VALUES (from_account_id, to_account_id, amount);

    RETURN TRUE;

EXCEPTION WHEN OTHERS THEN
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;