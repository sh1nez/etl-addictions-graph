-- Повышение зарплаты всем сотрудникам из отдела IT на 10%
UPDATE employees
SET salary = salary * 1.10
WHERE department = 'IT';

-- Изменение отдела сотрудника с id=1
UPDATE employees
SET department = 'Finance'
WHERE id = 1;