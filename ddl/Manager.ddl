CREATE TABLE Manager (
    manager_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    hire_date DATE NOT NULL,
    salary INT NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    department VARCHAR(100),
    exp_years INT,
    specialization VARCHAR(100),
    skills DECIMAL(4, 1)
);

INSERT INTO Manager (manager_id, first_name, last_name, full_name, birth_date, hire_date, salary, phone_number, email, address, department, exp_years, specialization, skills)
VALUES
(1, 'Анна', 'Кузнецова', '', '1985-04-20', '2013-05-10', '', '+71234567890', 'anna.kuznetsova@vetclinic.com', 'Москва, ул. Голубиная, д. 5', 'Veterinary', 10, 'Управление клиникой', ''),
(2, 'Сергей', 'Иванов', '', '1979-09-15', '2011-08-22', '', '+79876543210', 'sergey.ivanov@vetclinic.com', 'Санкт-Петербург, ул. Сизовая, д. 15', 'Veterinary', 12, 'Финансовое управление', ''),
(3, 'Екатерина', 'Петрова', '', '1988-12-05', '2015-03-30', '', '+71239876543', 'ekaterina.petrova@vetclinic.com', 'Казань, ул. Пернатых, д. 20', 'Veterinary', 8, 'Маркетинг и PR', ''),
(4, 'Александр', 'Смирнов', '', '1983-07-30', '2014-06-15', '', '+73216549870', 'alexander.smirnov@vetclinic.com', 'Новосибирск, ул. Крылатая, д. 25', 'Veterinary', 9, 'Операционное управление', ''),
(5, 'Виктория', 'Федорова', '', '1990-02-10', '2016-09-01', '', '+74561237890', 'victoria.fedorova@vetclinic.com', 'Екатеринбург, ул. Голубиный, д. 35', 'Veterinary', 7, 'Кадровое управление', ''),
(6, 'Максим', 'Волков', '', '1986-11-25', '2012-04-05', '', '+76549873210', 'maxim.volkov@vetclinic.com', 'Ростов-на-Дону, ул. Пернатых, д. 45', 'Veterinary', 11, 'Логистика и снабжение', ''),
(7, 'Ольга', 'Соколова', '', '1987-03-12', '2017-07-15', '', '+79876543211', 'olga.sokolova@vetclinic.com', 'Нижний Новгород, ул. Лесная, д. 10', 'Veterinary', 6, 'Информационные технологии', ''),
(8, 'Дмитрий', 'Морозов', '', '1982-08-23', '2010-11-30', '', '+71234567891', 'dmitry.morozov@vetclinic.com', 'Самара, ул. Речная, д. 22', 'Veterinary', 13, 'Стратегическое планирование', ''),
(9, 'Мария', 'Лебедева', '', '1991-05-18', '2018-02-20', '', '+73216549871', 'maria.lebedeva@vetclinic.com', 'Краснодар, ул. Полевая, д. 30', 'Veterinary', 5, 'Клиентский сервис', ''),
(10, 'Игорь', 'Николаев', '', '1984-10-05', '2015-04-10', '', '+74561237891', 'igor.nikolaev@vetclinic.com', 'Воронеж, ул. Садовая, д. 40', 'Veterinary', 8, 'Юридическое сопровождение', ''),
(11, 'Ирина', 'Захарова', '', '1989-06-14', '2014-07-20', '', '+79876543212', 'irina.zakharova@vetclinic.com', 'Москва, ул. Лесная, д. 15', 'Veterinary', 9, 'Финансовое управление', ''),
(12, 'Алексей', 'Кузьмин', '', '1981-04-03', '2012-09-10', '', '+71234567892', 'alexey.kuzmin@vetclinic.com', 'Санкт-Петербург, ул. Речная, д. 20', 'Veterinary', 11, 'Маркетинг и PR', ''),
(13, 'Юлия', 'Соловьева', '', '1992-11-28', '2017-08-05', '', '+73216549872', 'yulia.solovyeva@vetclinic.com', 'Казань, ул. Полевая, д. 25', 'Veterinary', 6, 'Кадровое управление', ''),
(14, 'Андрей', 'Васильев', '', '1985-03-07', '2015-05-12', '', '+74561237892', 'andrey.vasilyev@vetclinic.com', 'Новосибирск, ул. Лесная, д. 30', 'Veterinary', 8, 'Логистика и снабжение', ''),
(15, 'Наталья', 'Павлова', '', '1987-09-22', '2016-10-20', '', '+76549873211', 'natalia.pavlova@vetclinic.com', 'Екатеринбург, ул. Речная, д. 35', 'Veterinary', 7, 'Информационные технологии', '');

UPDATE Manager
SET salary = CASE
    WHEN specialization IN ('Кадровое управление', 'Маркетинг и PR', 'Юридическое сопровождение') THEN 112000
    WHEN specialization IN ('Финансовое управление', 'Клиентский сервис', 'Логистика и снабжение') THEN 73000
    WHEN specialization IN ('Информационные технологии', 'Операционное управление', 'Стратегическое планирование') THEN 95700
    WHEN specialization = 'Управление клиникой' THEN 205000
    ELSE salary
END;

UPDATE Manager
SET full_name = CONCAT(first_name, ' ', last_name);

UPDATE Manager
SET email = REPLACE(REPLACE(email, 'sergey.ivanov@vetclinic.com', 'Ivanus228@vetclinic.com'), 'maxim.volkov@vetclinic.com', 'volkAUF@vetclinic.com');

UPDATE Manager
SET salary = ROUND(salary * 1.10)
WHERE exp_years > 9;

UPDATE Manager
SET phone_number =
    CONCAT('+',
    SUBSTRING(phone_number, 2, 1), '-',
    SUBSTRING(phone_number, 3, 3), '-',
    SUBSTRING(phone_number, 6, 3), '-',
    SUBSTRING(phone_number, 9, 2), '-',
    SUBSTRING(phone_number, 11, 2));

UPDATE Manager
SET skills = CASE
    WHEN ROUND((100.0 / (SELECT MAX(exp_years) FROM Manager)) * exp_years * (0.9 + abs(RANDOM() / 9223372036854775807.0) * 0.2), 1) <= 0 THEN 0
    WHEN ROUND((100.0 / (SELECT MAX(exp_years) FROM Manager)) * exp_years * (0.9 + abs(RANDOM() / 9223372036854775807.0) * 0.2), 1) >= 100 THEN 100
    ELSE ROUND((100.0 / (SELECT MAX(exp_years) FROM Manager)) * exp_years * (0.9 + abs(RANDOM() / 9223372036854775807.0) * 0.2), 1)
END;

UPDATE Manager
SET salary = salary + 7000
WHERE skills > 94.5;

UPDATE Manager
SET skills = CEIL(skills);

UPDATE Manager
SET address =
    SUBSTR(address, 1, INSTR(address, ',') - 1) || ', ' ||
    TRIM(REPLACE(SUBSTR(address, INSTR(address, ',') + 1, INSTR(SUBSTR(address, INSTR(address, ',') + 1), ',') - 1), 'ул. ', '')) || '' ||
    TRIM(REPLACE(SUBSTR(address, INSTR(SUBSTR(address, INSTR(address, ',') + 1), ',') + INSTR(address, ',')), 'д. ', ''));

UPDATE Manager 
SET hire_date = strftime('%Y-%m', hire_date)
