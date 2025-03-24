-- Добавление новых сотрудников
INSERT INTO employees (employee_id, name, email, position)
SELECT 
    h.id,
    h.full_name,
    h.contact_email,
    h.job_title
FROM hired_employees h
LEFT JOIN employees e ON h.id = e.employee_id
WHERE e.employee_id IS NULL;
