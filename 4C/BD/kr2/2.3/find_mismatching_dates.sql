CREATE OR REPLACE FUNCTION fix_mismatching_dates_valekzhanin()
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_p record;
    v_s record;
BEGIN
    FOR v_p IN SELECT * FROM property LOOP
        FOR v_s IN SELECT * FROM sale WHERE property_id = v_p.id LOOP
            RAISE NOTICE '%', v_p.listing_date < v_s.sale_date;
            IF v_p.listing_date > v_s.sale_date THEN
                RAISE WARNING 'Квартира была продана раньше, чем была выставлена на продажу --> продана %, выставлена %', v_s.sale_date, v_p.listing_date;
            END IF;
        END LOOP;
    END LOOP;
END;
$$;