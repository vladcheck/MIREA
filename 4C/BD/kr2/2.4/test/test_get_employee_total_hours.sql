-- Проверка для сотрудника 100 (ожидается переработка)
SELECT get_employee_total_hours_valekzhanin(100);

-- Проверка для сотрудника 101 (ожидается норма)
SELECT get_employee_total_hours_valekzhanin(101);

-- Проверка для сотрудника 104 (ожидается меньше нормы)
SELECT get_employee_total_hours_valekzhanin(104);