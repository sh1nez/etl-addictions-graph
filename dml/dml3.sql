-- Создаем таблицу для примера
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    department VARCHAR(50),
    salary DECIMAL(10, 2)
);

-- Вставляем несколько строк за одну операцию
INSERT INTO employees (id, name, department, salary)
VALUES
    (1, 'Иван Иванов', 'HR', 50000.00),
    (2, 'Петр Петров', 'IT', 75000.00),
    (3, 'Сидор Сидоров', 'IT', 80000.00),
    (4, 'Мария Кузнецова', 'HR', 55000.00);

-- Обновляем зарплату всем сотрудникам IT-отдела на 10%
UPDATE employees
SET salary = salary * 1.10
WHERE department = 'IT';