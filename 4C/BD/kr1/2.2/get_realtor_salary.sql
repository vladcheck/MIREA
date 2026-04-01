CREATE OR REPLACE FUNCTION get_realtor_salary_valekzhanin(
    p_coefficient DECIMAL(10,2),
    p_bonus DECIMAL(10,2),
    p_month INTEGER,
    p_year INTEGER,
    p_realtor_last_name VARCHAR(255)
)
RETURNS DECIMAL(10,2)
AS $$
DECLARE
    v_total_sales DECIMAL(10,2);
    v_salary DECIMAL(10,2);
    v_realtor_id INTEGER;
BEGIN
    -- Получаем ID риэлтора по фамилии
    SELECT id INTO v_realtor_id
    FROM realtor
    WHERE last_name = p_realtor_last_name;
    
    -- Проверяем, найден ли риэлтор
    IF v_realtor_id IS NULL THEN
        RAISE EXCEPTION 'Риэлтор с фамилией % не найден', p_realtor_last_name;
    END IF;
    
    -- Рассчитываем общую сумму проданных объектов за указанный месяц
    SELECT COALESCE(SUM(price), 0) INTO v_total_sales
    FROM sale
    WHERE realtor_id = v_realtor_id
      AND EXTRACT(MONTH FROM sale_date) = p_month
      AND EXTRACT(YEAR FROM sale_date) = p_year;
    
    -- Рассчитываем зарплату по формуле N*S+R
    v_salary := v_total_sales * p_coefficient + p_bonus;
    
    RETURN v_salary;
END;
$$ LANGUAGE plpgsql;