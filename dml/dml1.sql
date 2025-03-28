-- Вставка нового сотрудника
INSERT INTO employees (name, department, salary)
VALUES ('Иван Иванов', 'IT', 75000.00);

-- Вставка с использованием DEFAULT для hire_date
INSERT INTO employees (name, department, salary, hire_date)
VALUES ('Мария Петрова', 'HR', 65000.00, DEFAULT);