SELECT 
    employee_id AS "ID сотрудника",
    get_salary_valekzhanin(employee_id, 100) AS "Расчетная зарплата",
    100 AS "Базовая ставка"
FROM (
    SELECT DISTINCT employee_id 
    FROM work_day_valekzhanin 
    ORDER BY employee_id
) AS employees;