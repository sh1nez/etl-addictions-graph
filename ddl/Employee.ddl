CREATE TABLE Employee (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    hire_date DATE NOT NULL,
    position VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    supervisor_id INT,
    department VARCHAR(100),
    experience_years INT,
    FOREIGN KEY (supervisor_id) REFERENCES Employee(employee_id)
);


INSERT INTO Employee (employee_id, first_name, last_name, birth_date, hire_date, position, salary, phone_number, email, address, supervisor_id, department, experience_years) VALUES
(1, 'Ivan', 'Ivanov', '1980-05-15', '2010-06-01', 'Главный тренер', 85000.00, '+79000000001', 'ivan@pigeonfarm.com', 'Москва, ул. Голубиная 5', 1, 'Тренировка', 13),
(2, 'Olga', 'Petrova', '1985-08-22', '2015-03-10', 'Старший ветеринар', 75000.00, '+79000000002', 'olga@pigeonfarm.com', 'Санкт-Петербург, пер. Крылатый 12', 1, 'Здоровье', 8),
(3, 'Sergey', 'Sidorov', '1990-12-10', '2018-07-15', 'Управляющий фермой', 68000.00, '+79000000003', 'sergey@pigeonfarm.com', 'Казань, пр. Пернатых 20', 1, 'Администрация', 5),
(4, 'Anna', 'Smirnova', '1992-03-05', '2019-11-20', 'Тренер по полетам', 62000.00, '+79000000004', 'anna@pigeonfarm.com', 'Новосибирск, ул. Гнездовая 7', 1, 'Тренировка', 4),
(5, 'Dmitry', 'Kozlov', '1988-07-12', '2016-09-01', 'Специалист по кормлению', 58000.00, '+79000000005', 'dmitry@pigeonfarm.com', 'Сочи, ул. Кормовая 15', 3, 'Питание', 7),
(6, 'Maria', 'Pavlova', '1995-09-09', '2021-08-15', 'Младший тренер', 45000.00, '+79000000006', 'maria@pigeonfarm.com', 'Ростов-на-Дону, ул. Полетная 3', 4, 'Тренировка', 2),
(7, 'Alexey', 'Morozov', '1993-04-18', '2022-02-01', 'Диетолог', 53000.00, '+79000000007', 'alexey@pigeonfarm.com', 'Калининград, пр. Витаминный 8', 5, 'Питание', 1),
(8, 'Elena', 'Fedorova', '1989-11-28', '2019-04-12', 'Инспектор по разведению', 61000.00, '+79000000008', 'elena@pigeonfarm.com', 'Владивосток, ул. Селекционная 11', 3, 'Разведение', 4),
(9, 'Andrey', 'Volkov', '1996-06-30', '2020-05-10', 'Сотрудник по логистике', 48000.00, '+79000000009', 'andrey@pigeonfarm.com', 'Екатеринбург, ш. Транспортное 9', 3, 'Логистика', 3),
(10, 'Natalia', 'Orlova', '1994-01-25', '2023-03-22', 'Ассистент ветеринара', 42000.00, '+79000000011', 'natalia@pigeonfarm.com', 'Самара, ул. Медицинская 16', 2, 'Здоровье', 0),
(11, 'Viktor', 'Lebedev', '1991-08-14', '2017-09-01', 'Тренер-наставник', 67000.00, '+79000000012', 'vikto@pigeonfarm.com', 'Краснодар, ул. Стартовая 22', 1, 'Тренировка', 6),
(12, 'Tatiana', 'Sorokina', '1987-05-03', '2014-11-15', 'Заведующая кормлением', 64000.00, '+79000000013', 'tatiana@pigeonfarm.com', 'Уфа, пр. Зерновой 45', 5, 'Питание', 9),
(13, 'Pavel', 'Golubev', '1998-02-19', '2022-07-10', 'Стажер тренера', 38000.00, '+79000000014', 'pavel@pigeonfarm.com', 'Воронеж, ул. Юннатская 13', 6, 'Тренировка', 1),
(14, 'Alina', 'Vorobyeva', '1990-12-05', '2016-04-20', 'Генетик-селекционер', 71000.00, '+79000000015', 'alina@pigeonfarm.com', 'Тюмень, ул. Научная 18', 8, 'Разведение', 7),
(15, 'Mikhail', 'Sokolov', '1983-10-30', '2012-08-01', 'Главный по снаряжению', 69000.00, '+79000000016', 'mikhail@pigeonfarm.com', 'Пермь, пр. Снарядный 29', 3, 'Логистика', 11);


SELECT *
FROM Employee
WHERE department = 'Тренировка';


SELECT first_name, position
FROM Employee
WHERE salary > 50000;


UPDATE Employee
SET phone_number = '+79000000017'
WHERE employee_id = 7;


DELETE FROM Employee
WHERE position = 'Стажер тренера';


SELECT first_name, last_name, hire_date
FROM Employee
WHERE hire_date BETWEEN '2023-01-01' AND '2023-12-31';


SELECT COUNT(*) AS total_employees
FROM Employee;


SELECT first_name, last_name, hire_date
FROM Employee
ORDER BY hire_date DESC
LIMIT 3;


SELECT
    e.first_name,
    e.last_name,
    e.salary,
    e.department,
    dep_avg.avg_salary
FROM Employee e
JOIN (
    SELECT
        department,
        AVG(salary) AS avg_salary
    FROM Employee
    GROUP BY department
) dep_avg ON e.department = dep_avg.department
WHERE e.salary > dep_avg.avg_salary;


SELECT *
FROM Employee
WHERE first_name = 'Anna';


SELECT DISTINCT position
FROM Employee
ORDER BY position ASC;


SELECT *
FROM (
    SELECT
        *,
        RANK() OVER (PARTITION BY department ORDER BY experience_years DESC) AS rank
    FROM Employee
) AS ranked
WHERE rank <= 3;


UPDATE Employee
SET address = 'Москва, ул. Новая 10'
WHERE address LIKE 'Москва%';


DELETE FROM Employee
WHERE salary < 40000;


SELECT
    email,
    COUNT(*) AS duplicates
FROM Employee
GROUP BY email
HAVING COUNT(*) > 1;


SELECT last_name, birth_date
FROM Employee
WHERE birth_date < CURRENT_DATE - INTERVAL '40 years';


UPDATE Employee
SET salary = salary * 1.15
WHERE department = 'Тренировка'
  AND salary < (SELECT AVG(salary) FROM Employee);


UPDATE Employee
SET
    position = 'Тренер по полетам',
    department = 'Тренировка'
WHERE position = 'Младший тренер'
  AND experience_years > 2;
