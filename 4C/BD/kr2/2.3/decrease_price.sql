CREATE OR REPLACE FUNCTION decrease_price_valekzhanin()
RETURNS void
AS $$
DECLARE
    v_p record;
    v_discount numeric := 0;
    v_avg_score numeric := 0;
    v_old_price numeric := 0;
    v_new_price numeric := 0;
    v_processed_count integer := 0;
    v_discounted_count integer := 0;
BEGIN
    v_processed_count := 0;
    v_discounted_count := 0;

    FOR v_p IN SELECT * FROM property LOOP
        v_discount := 0;
        v_processed_count := v_processed_count + 1;

        SELECT COALESCE(AVG(score), 0)
        INTO v_avg_score
        FROM evaluation
        WHERE property_id = v_p.id;

        v_old_price := v_p.price;

        IF v_p.listing_date < CURRENT_DATE - INTERVAL '12 months' AND v_avg_score < 4 THEN
            v_discount := 0.20;  -- 20%
        ELSIF v_p.listing_date < CURRENT_DATE - INTERVAL '9 months' AND v_avg_score < 5 THEN
            v_discount := 0.10;  -- 10%
        ELSIF v_p.listing_date < CURRENT_DATE - INTERVAL '6 months' AND v_avg_score < 6 THEN
            v_discount := 0.05;  -- 5%
        END IF;

        IF v_discount > 0 THEN
            v_new_price := v_p.price * (1 - v_discount);

            UPDATE property
            SET price = v_new_price
            WHERE id = v_p.id;

            v_discounted_count := v_discounted_count + 1;

            RAISE NOTICE 'Объект %: цена % -> % (скидка % процентов, средний балл %)',
                v_p.id, v_old_price, v_new_price, v_discount * 100, v_avg_score;
        END IF;
    END LOOP;

    RAISE NOTICE 'Всего обработано объектов: %', v_processed_count;
    RAISE NOTICE 'Применено скидок: %', v_discounted_count;
END;
$$ LANGUAGE plpgsql;