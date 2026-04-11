-- Проверка для сотрудника 100 (ожидается переработка)
SELECT get_employee_total_hours_valekzhanin(100);

-- Проверка для сотрудника 102 (ожидается норма)
SELECT get_employee_total_hours_valekzhanin(102);

-- Проверка для сотрудника 104 (ожидается меньше нормы)
SELECT get_employee_total_hours_valekzhanin(104);