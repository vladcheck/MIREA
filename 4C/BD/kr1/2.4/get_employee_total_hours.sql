CREATE OR REPLACE FUNCTION get_employee_total_hours_valekzhanin(
    p_id numeric
)
RETURNS void
AS $$
DECLARE
    c_enter CONSTANT integer := 1;
    c_leave CONSTANT integer := 2;
    v_prev_gate_log record;
    v_is_prev_date_assigned boolean := false;
    v_gate_log record;
    v_total_work_hours numeric(5,2) := 0;
    v_interval_seconds numeric := 0;
BEGIN
    FOR v_gate_log IN
        SELECT *
        FROM work_day_valekzhanin w
        WHERE w.employee_id = p_id
        ORDER BY w.gate_log, w.card_reader_value
    LOOP
        IF v_is_prev_date_assigned = true THEN
            IF v_prev_gate_log.card_reader_value = c_enter AND
                v_gate_log.card_reader_value = c_leave THEN
                v_interval_seconds := EXTRACT(EPOCH FROM (v_gate_log.gate_log - v_prev_gate_log.gate_log));

                v_total_work_hours := v_total_work_hours + (v_interval_seconds / 3600.0);
            END IF;
        END IF;

        v_prev_gate_log := v_gate_log;

        IF v_is_prev_date_assigned = false THEN
            v_is_prev_date_assigned := true;
        END IF;
    END LOOP;

    IF v_total_work_hours > 40 THEN
        RAISE NOTICE 'Сотрудник %: Больше нормы (% часов)', p_id, v_total_work_hours;
    ELSIF v_total_work_hours = 40 THEN
        RAISE NOTICE 'Сотрудник %: Норма (% часов)', p_id, v_total_work_hours;
    ELSE
        RAISE NOTICE 'Сотрудник %: Меньше нормы (% часов)', p_id, v_total_work_hours;
    END IF;
END;
$$ LANGUAGE plpgsql;