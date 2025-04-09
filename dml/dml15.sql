-- Изменение уровня доступа сотрудников
UPDATE employees
SET access_level = 'Admin'
WHERE hired_date < NOW() - INTERVAL '5 years' AND department = 'Finance';
