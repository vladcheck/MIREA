CREATE OR REPLACE FUNCTION find_mismatching_dates_valekzhanin()
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_anomaly_found boolean := false;
    v_p record;
    v_s record;
BEGIN
    FOR v_p IN SELECT * FROM property LOOP
        FOR v_s IN SELECT * FROM sale WHERE property_id = v_p.id LOOP
            IF v_p.listing_date > v_s.sale_date THEN
                v_anomaly_found := true;
                RAISE WARNING 'Квартира была продана раньше, чем была выставлена на продажу --> продана %, выставлена %', v_s.sale_date, v_p.listing_date;
            END IF;
        END LOOP;
    END LOOP;

    IF NOT v_anomaly_found THEN
        RAISE NOTICE 'Аномалий не обнаружено.';
    END IF;
END;
$$;