CREATE TABLE PigeonLoft (
    loft_id SERIAL PRIMARY KEY,
    loft_name VARCHAR(100) NOT NULL,
    manager_id INT,
    location TEXT NOT NULL,
    capacity INT NOT NULL,
    established_date DATE,
    FOREIGN KEY (manager_id) REFERENCES Manager(manager_id)
);

INSERT INTO PigeonLoft (loft_name, location, capacity, established_date) VALUES
    ('Небесное Пристанище', 'Москва, Россия', 50, '2005-06-15'),
    ('Уютное Гнездо', 'Санкт-Петербург, Россия', 75, '2010-09-23'),
    ('Крылатый Оазис', 'Новосибирск, Россия', 60, '2008-04-12'),
    ('Лазурный Голубятник', 'Екатеринбург, Россия', 90, '2015-07-08'),
    ('Облачный Край', 'Казань, Россия', 40, '2012-02-19'),
    ('Высотный Полет', 'Нижний Новгород, Россия', 85, '2018-05-14'),
    ('Горизонт', 'Челябинск, Россия', 100, '2000-11-30'),
    ('Гнездо Свободы', 'Омск, Россия', 70, '2016-08-21'),
    ('Рай для Голубей', 'Ростов-на-Дону, Россия', 55, '2011-03-10'),
    ('Прохладный Насест', 'Уфа, Россия', 65, '2013-09-05'),
    ('Высокий Полет', 'Волгоград, Россия', 80, '2017-12-25'),
    ('Голубиный Панорамник', 'Пермь, Россия', 95, '2009-06-01'),
    ('Гребень Крыльев', 'Красноярск, Россия', 50, '2014-11-17'),
    ('Голубиный Угол', 'Воронеж, Россия', 85, '2007-10-09'),
    ('Тихое Гнездышко', 'Саратов, Россия', 45, '2019-07-14'),
    ('Вольер', 'Краснодар, Россия', 110, '2002-01-29'),
    ('Ветреный Голубятник', 'Тольятти, Россия', 60, '2015-05-22'),
    ('Крылатое Небо', 'Ижевск, Россия', 75, '2003-09-18'),
    ('Золотые Крылья', 'Барнаул, Россия', 100, '2006-12-11'),
    ('Закатный Голубятник', 'Тюмень, Россия', 50, '2020-03-01');

update PigeonLoft
set manager_id = 1
where capacity <= 50;

update PigeonLoft
set manager_id = 2
where capacity <= 80 and capacity > 50;

update PigeonLoft
set manager_id = 3
where manager_id is null;

UPDATE PigeonLoft
SET location = CONCAT(UPPER(location), LOWER(location))
WHERE manager_id = 1;

DELETE FROM PigeonLoft
WHERE established_date < DATE '2005-09-23';

INSERT INTO PigeonLoft (loft_name, location, capacity, established_date)
SELECT
    loft_name,
    UPPER(location),
    CAST(capacity AS INT),
    TO_DATE(TO_CHAR(established_date, 'YYYY-MM-DD'), 'YYYY-MM-DD')
FROM PigeonLoft
WHERE manager_id = 1;

UPDATE PigeonLoft
SET established_date = established_date + INTERVAL '1 year'
WHERE capacity > 60;

DELETE FROM PigeonLoft
WHERE location IN ('Саратов, Россия', 'Тюмень, Россия');

INSERT INTO PigeonLoft (loft_name, location, capacity, established_date)
select loft_name, Upper(location), capacity, established_date	from PigeonLoft
where capacity = 50;
