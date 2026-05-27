CREATE OR REPLACE FUNCTION calc_arrival_time_valekzhanin(p_departure TIMESTAMP, p_duration INTERVAL)
RETURNS TIMESTAMP AS $$
BEGIN
    RETURN p_departure + p_duration;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION is_trip_today_valekzhanin(p_frequency VARCHAR)
RETURNS INT AS $$
DECLARE
    v_today DATE := CURRENT_DATE;
    v_day_part INT;
    v_dow VARCHAR(3);
BEGIN
    v_day_part := EXTRACT(DAY FROM v_today);
    v_dow := TO_CHAR(v_today, 'dy');

    CASE lower(trim(p_frequency))
        WHEN 'ежедн.', 'daily' THEN RETURN 1;
        WHEN 'четн.', 'even' THEN RETURN CASE WHEN v_day_part % 2 = 0 THEN 1 ELSE 0 END;
        WHEN 'нечет.', 'odd' THEN RETURN CASE WHEN v_day_part % 2 <> 0 THEN 1 ELSE 0 END;
        WHEN 'пн', 'mon' THEN RETURN CASE WHEN v_dow = 'mon' THEN 1 ELSE 0 END;
        WHEN 'вт', 'tue' THEN RETURN CASE WHEN v_dow = 'tue' THEN 1 ELSE 0 END;
        WHEN 'ср', 'wed' THEN RETURN CASE WHEN v_dow = 'wed' THEN 1 ELSE 0 END;
        WHEN 'чт', 'thu' THEN RETURN CASE WHEN v_dow = 'thu' THEN 1 ELSE 0 END;
        WHEN 'пт', 'fri' THEN RETURN CASE WHEN v_dow = 'fri' THEN 1 ELSE 0 END;
        WHEN 'сб', 'sat' THEN RETURN CASE WHEN v_dow = 'sat' THEN 1 ELSE 0 END;
        WHEN 'вс', 'sun' THEN RETURN CASE WHEN v_dow = 'sun' THEN 1 ELSE 0 END;
        ELSE RETURN 0;
    END CASE;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION format_fio_valekzhanin(p_full_name VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    parts TEXT[];
BEGIN
    parts := string_to_array(trim(p_full_name), ' ');
    IF array_length(parts, 1) >= 3 THEN
        RETURN parts[1] || ' ' || upper(substring(parts[2], 1, 1)) || '.' || upper(substring(parts[3], 1, 1)) || '.';
    ELSIF array_length(parts, 1) = 2 THEN
        RETURN parts[1] || ' ' || upper(substring(parts[2], 1, 1)) || '.';
    ELSIF array_length(parts, 1) = 1 THEN
        RETURN parts[1];
    ELSE
        RETURN '';
    END IF;
END;
$$ LANGUAGE plpgsql;
