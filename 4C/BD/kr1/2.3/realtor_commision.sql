CREATE OR REPLACE FUNCTION realtor_commision_valekzhanin()
RETURNS void
AS $$
DECLARE
    v_sale record;
    v_commission numeric := 0;
    v_sale_price numeric := 0;
    v_commission_rate numeric := 0;
    v_processed_count integer := 0;
    v_realtor_full_name text;
BEGIN
    ALTER TABLE sale ADD COLUMN IF NOT EXISTS commission DOUBLE PRECISION;
    v_processed_count := 0;

    FOR v_sale IN
        SELECT
            s.id,
            s.price,
            s.realtor_id,
            r.last_name,
            r.first_name,
            r.middle_name
        FROM sale s
        JOIN realtor r ON s.realtor_id = r.id
        ORDER BY s.id
    LOOP
        v_processed_count := v_processed_count + 1;
        v_sale_price := v_sale.price;
        v_commission := 0;

        -- Формируем полное имя риэлтора
        v_realtor_full_name := v_sale.last_name || ' ' || v_sale.first_name;
        IF v_sale.middle_name IS NOT NULL THEN
            v_realtor_full_name := v_realtor_full_name || ' ' || v_sale.middle_name;
        END IF;

        IF v_sale_price < 1000000 THEN
            -- До 1 млн. руб. – 2%
            v_commission_rate := 0.02;
        ELSIF v_sale_price >= 1000000 AND v_sale_price < 3000000 THEN
            -- От 1 млн. до 3 млн. руб. – 1,9%
            v_commission_rate := 0.019;
        ELSE
            -- От 3 млн. руб. – 1,7%
            v_commission_rate := 0.017;
        END IF;

        v_commission := v_sale_price * v_commission_rate;

        -- Обновление записи в таблице sale
        UPDATE sale
        SET commission = v_commission
        WHERE id = v_sale.id;

        -- Логирование результата
        RAISE NOTICE 'Продажа %: риэлтор %, цена %, комиссия % процентов = %',
            v_sale.id, v_realtor_full_name, v_sale_price,
            v_commission_rate * 100, v_commission;
    END LOOP;

    RAISE NOTICE 'Всего обработано продаж: %', v_processed_count;
END;
$$ LANGUAGE plpgsql;