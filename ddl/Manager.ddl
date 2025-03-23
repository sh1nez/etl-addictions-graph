CREATE TABLE Manager (
    manager_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    department VARCHAR(100),
    experience_years INT,
    specialization VARCHAR(100)
);

INSERT INTO Manager (manager_id, first_name, last_name, birth_date, hire_date, salary, phone_number, email, address, department, experience_years, specialization)
VALUES
(1, 'Анна', 'Кузнецова', '1985-04-20', '2013-05-10', 65000.00, '+71234567890', 'anna.kuznetsova@vetclinic.com', 'Москва, ул. Голубиная, д. 5', 'Veterinary', 10, 'Управление клиникой'),
(2, 'Сергей', 'Иванов', '1979-09-15', '2011-08-22', 70000.00, '+79876543210', 'sergey.ivanov@vetclinic.com', 'Санкт-Петербург, ул. Сизовая, д. 15', 'Veterinary', 12, 'Финансовое управление'),
(3, 'Екатерина', 'Петрова', '1988-12-05', '2015-03-30', 60000.00, '+71239876543', 'ekaterina.petrova@vetclinic.com', 'Казань, ул. Пернатых, д. 20', 'Veterinary', 8, 'Маркетинг и PR'),
(4, 'Александр', 'Смирнов', '1983-07-30', '2014-06-15', 68000.00, '+73216549870', 'alexander.smirnov@vetclinic.com', 'Новосибирск, ул. Крылатая, д. 25', 'Veterinary', 9, 'Операционное управление'),
(5, 'Виктория', 'Федорова', '1990-02-10', '2016-09-01', 62000.00, '+74561237890', 'victoria.fedorova@vetclinic.com', 'Екатеринбург, ул. Голубиный, д. 35', 'Veterinary', 7, 'Кадровое управление'),
(6, 'Максим', 'Волков', '1986-11-25', '2012-04-05', 67000.00, '+76549873210', 'maxim.volkov@vetclinic.com', 'Ростов-на-Дону, ул. Пернатых, д. 45', 'Veterinary', 11, 'Логистика и снабжение'),
(7, 'Ольга', 'Соколова', '1987-03-12', '2017-07-15', 63000.00, '+79876543211', 'olga.sokolova@vetclinic.com', 'Нижний Новгород, ул. Лесная, д. 10', 'Veterinary', 6, 'Информационные технологии'),
(8, 'Дмитрий', 'Морозов', '1982-08-23', '2010-11-30', 72000.00, '+71234567891', 'dmitry.morozov@vetclinic.com', 'Самара, ул. Речная, д. 22', 'Veterinary', 13, 'Стратегическое планирование'),
(9, 'Мария', 'Лебедева', '1991-05-18', '2018-02-20', 61000.00, '+73216549871', 'maria.lebedeva@vetclinic.com', 'Краснодар, ул. Полевая, д. 30', 'Veterinary', 5, 'Клиентский сервис'),
(10, 'Игорь', 'Николаев', '1984-10-05', '2015-04-10', 66000.00, '+74561237891', 'igor.nikolaev@vetclinic.com', 'Воронеж, ул. Садовая, д. 40', 'Veterinary', 8, 'Юридическое сопровождение'),
(11, 'Ирина', 'Захарова', '1989-06-14', '2014-07-20', 64000.00, '+79876543212', 'irina.zakharova@vetclinic.com', 'Москва, ул. Лесная, д. 15', 'Veterinary', 9, 'Финансовое управление'),
(12, 'Алексей', 'Кузьмин', '1981-04-03', '2012-09-10', 69000.00, '+71234567892', 'alexey.kuzmin@vetclinic.com', 'Санкт-Петербург, ул. Речная, д. 20', 'Veterinary', 11, 'Маркетинг и PR'),
(13, 'Юлия', 'Соловьева', '1992-11-28', '2017-08-05', 63000.00, '+73216549872', 'yulia.solovyeva@vetclinic.com', 'Казань, ул. Полевая, д. 25', 'Veterinary', 6, 'Кадровое управление'),
(14, 'Андрей', 'Васильев', '1985-03-07', '2015-05-12', 67000.00, '+74561237892', 'andrey.vasilyev@vetclinic.com', 'Новосибирск, ул. Лесная, д. 30', 'Veterinary', 8, 'Логистика и снабжение'),
(15, 'Наталья', 'Павлова', '1987-09-22', '2016-10-20', 62000.00, '+76549873211', 'natalia.pavlova@vetclinic.com', 'Екатеринбург, ул. Речная, д. 35', 'Veterinary', 7, 'Информационные технологии');

UPDATE Manager
SET salary = 97400.00
WHERE manager_id IN (1, 2, 5);

SELECT *
FROM Manager 
ORDER BY experience_years DESC;

SELECT department, COUNT(*) AS manager_count
FROM Manager
GROUP BY department;

SELECT department, AVG(salary) AS average_salary
FROM Manager
GROUP BY department;

SELECT department, specialization, COUNT(*) AS manager_count
FROM Manager
GROUP BY department, specialization
HAVING COUNT(*) > 0;

ALTER TABLE Manager
ADD COLUMN skills DECIMAL(4, 1) CHECK (skills >= 0 AND skills <= 100);

UPDATE Manager
SET skills = CASE
    WHEN manager_id = 1 THEN 91.7
    WHEN manager_id = 2 THEN 78.3
    WHEN manager_id = 3 THEN 63.8
    WHEN manager_id = 4 THEN 57.9
    WHEN manager_id = 5 THEN 63.5
    WHEN manager_id = 6 THEN 83.6
    WHEN manager_id = 7 THEN 76.7
    WHEN manager_id = 8 THEN 45.7
    WHEN manager_id = 9 THEN 72.1
    WHEN manager_id = 10 THEN 61.9
    WHEN manager_id = 11 THEN 82.3
    WHEN manager_id = 12 THEN 84.4
    WHEN manager_id = 13 THEN 58.3
    WHEN manager_id = 14 THEN 77.4
    WHEN manager_id = 15 THEN 93.2
END;

SELECT *
FROM Manager
ORDER BY skills DESC
LIMIT 10;

SELECT CONCAT(first_name, ' ', last_name) AS full_name
FROM Manager;

ALTER TABLE Manager 
DROP COLUMN hire_date;

DROP TABLE Manager
