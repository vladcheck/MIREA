CREATE OR REPLACE FUNCTION get_salary_valekzhanin(
    p_employee_id numeric,
    p_base_wage numeric
)
RETURNS numeric
AS $$
DECLARE
    c_enter CONSTANT integer := 1;
    c_exit CONSTANT integer := 2;

    v_log record;
    v_prev_log record;

    v_log_time time;
    v_prev_time time;
    v_log_date date;
    v_prev_date date;

    v_has_prev boolean := false;
    v_is_new_day boolean := false;

    v_late_minutes integer := 0;
    v_violations_count integer := 0;

    v_A numeric := 1.0;
    v_salary numeric := 0;

    v_work_start CONSTANT time := '09:00:00';
    v_lunch_start CONSTANT time := '13:00:00';
    v_lunch_end CONSTANT time := '14:00:00';
    v_work_end CONSTANT time := '18:00:00';
BEGIN
    FOR v_log IN
        SELECT w.employee_id, w.gate_log, w.card_reader_value
        FROM work_day_valekzhanin w
        WHERE w.employee_id = p_employee_id
        ORDER BY w.gate_log, w.card_reader_value
    LOOP
        v_log_time := v_log.gate_log::time;
        v_log_date := v_log.gate_log::date;

        v_is_new_day := false;

        IF v_has_prev THEN
            v_prev_time := v_prev_log.gate_log::time;
            v_prev_date := v_prev_log.gate_log::date;

            IF v_log_date != v_prev_date THEN
                v_is_new_day := true;
            END IF;
        END IF;

        IF v_log.card_reader_value = c_enter THEN
            IF v_is_new_day OR NOT v_has_prev THEN
                IF v_log_time > v_work_start THEN
                    v_late_minutes := EXTRACT(EPOCH FROM (v_log_time - v_work_start)) / 60;
                    v_violations_count := v_violations_count + CEIL(v_late_minutes / 10);
                    RAISE NOTICE 'Сотрудник % опоздал на смену на % мин (%)',
                        p_employee_id, v_late_minutes, v_log.gate_log;
                END IF;
            ELSIF v_log_time > v_lunch_end THEN
                v_late_minutes := EXTRACT(EPOCH FROM (v_log_time - v_lunch_end)) / 60;
                v_violations_count := v_violations_count + CEIL(v_late_minutes / 10);
                RAISE NOTICE 'Сотрудник % вернулся с обеда позже на % мин (%)',
                    p_employee_id, v_late_minutes, v_log.gate_log;
            END IF;

        ELSIF v_log.card_reader_value = c_exit THEN
            IF v_log_time < v_lunch_start THEN
                v_late_minutes := EXTRACT(EPOCH FROM (v_lunch_start - v_log_time)) / 60;
                v_violations_count := v_violations_count + CEIL(v_late_minutes / 10);
                RAISE NOTICE 'Сотрудник % ушел на обед раньше на % мин (%)',
                    p_employee_id, v_late_minutes, v_log.gate_log;
            ELSIF v_log_time < v_work_end AND v_log_time >= v_lunch_end THEN
                v_late_minutes := EXTRACT(EPOCH FROM (v_work_end - v_log_time)) / 60;
                v_violations_count := v_violations_count + CEIL(v_late_minutes / 10);
                RAISE NOTICE 'Сотрудник % ушел со смены раньше на % мин (%)',
                    p_employee_id, v_late_minutes, v_log.gate_log;
            END IF;
        END IF;

        v_prev_log := v_log;
        v_has_prev := true;
    END LOOP;


    v_A := 1.0 - (v_violations_count * 0.05);

    IF v_A < 0 THEN
        v_A := 0;
    END IF;

    v_salary := p_base_wage + p_base_wage * v_A;

    IF v_violations_count = 0 THEN
        RAISE NOTICE 'Нарушений не обнаружено, зарплата будет получена в полном размере.';
    END IF;

    RAISE NOTICE 'Коэффициент А: %', v_A;
    RAISE NOTICE 'Зарплата сотрудника %: % + % * % = %',
        p_employee_id, p_base_wage, p_base_wage, v_A, v_salary;

    RETURN v_salary;
END;
$$ LANGUAGE plpgsql;