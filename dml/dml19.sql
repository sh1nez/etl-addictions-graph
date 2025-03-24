-- Повышение зарплаты для менеджеров
UPDATE employees
SET salary = salary * 1.10
WHERE position = 'Manager'; 
