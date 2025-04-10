CREATE TABLE Pigeon (
    pigeon_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    breed VARCHAR(50),
    birth_date DATE,
    loft_id INT NOT NULL,
    owner_id INT,
    ring_number VARCHAR(20) UNIQUE,
    color VARCHAR(30),
    weight DECIMAL(5,2),
    flying_speed DECIMAL(5,2),
    training_hours INT,
    FOREIGN KEY (loft_id) REFERENCES PigeonLoft(loft_id),
    FOREIGN KEY (owner_id) REFERENCES Employee(employee_id)
);


INSERT INTO Pigeon (name, breed, birth_date, loft_id, owner_id, ring_number, color, weight, flying_speed, training_hours)
VALUES (
    'Thunder',
	'Racing',
	'2022-07-10',
	103,
	8,
    'RN-003',
	'Black',
	0.48,
	80.0,
	150
);

INSERT INTO Pigeon (name, breed, birth_date, loft_id, owner_id, ring_number, color, weight, flying_speed, training_hours)
SELECT
    'Sky',
	'Carrier',
	'2020-05-15',
    (SELECT loft_id FROM PigeonLoft WHERE loft_name = 'Sky Haven'),
    (SELECT employee_id FROM Employee WHERE first_name = 'John' AND last_name = 'Doe'),
    'RN-001',
	'White',
	0.45,
	60.5,
	120;

INSERT INTO Pigeon (name, breed, birth_date, loft_id, owner_id, ring_number, color, weight, flying_speed, training_hours)
VALUES (
    'Storm',
	'Homing',
	CURRENT_DATE - INTERVAL '1 year',
	105,
	12,
    'RN-005',
	'Grey',
	0.50,
	75.5,
	200
);

INSERT INTO Pigeon (name, breed, birth_date, loft_id, owner_id, ring_number, color, weight, flying_speed, training_hours)
VALUES (
    'Blaze',
	'Fantail',
	'2023-01-01',
	104,
	9,
    'RN-006',
	'Brown',
	0.42,
	65.0,
	90
)
ON CONFLICT (ring_number) DO NOTHING; -- Игнорировать дубликаты

INSERT INTO Pigeon (name, breed, birth_date, loft_id, owner_id, ring_number, color, weight, flying_speed, training_hours)
SELECT
    'Storm',
	'Homing',
	'2021-03-22',
    (SELECT loft_id FROM PigeonLoft WHERE location = 'Berlin'),
    (SELECT employee_id FROM Employee WHERE email = 'alice@example.com'),
    'RN-004',
	'Grey',
	0.52,
	75.0,
	200;

UPDATE Pigeon
SET owner_id = (SELECT employee_id FROM Employee WHERE first_name = 'Alice')
WHERE ring_number = 'RN-006';

UPDATE Pigeon
SET weight = 0.50, flying_speed = 85.5
WHERE ring_number = 'RN-005';

UPDATE Pigeon
SET training_hours = training_hours + 10
WHERE loft_id = 103;

UPDATE Pigeon
SET
    weight = weight * 1.05, -- Увеличить вес на 5%
    flying_speed = flying_speed + 5.0, -- Увеличить скорость на 5 км/ч
    loft_id = (
        SELECT loft_id
        FROM PigeonLoft
        WHERE location = 'Berlin' -- Новая голубятня в Берлине
    )
WHERE
    owner_id IN (
        SELECT employee_id
        FROM Employee
        WHERE department = 'Training' -- Сотрудники из отдела Training
    )
    AND loft_id IN (
        SELECT loft_id
        FROM PigeonLoft
        WHERE capacity > 100 -- Голубятни с вместимостью > 100
    )
    AND training_hours > 150 -- Более 150 часов тренировок
    AND EXISTS (
        SELECT 1
        FROM PigeonLoft
        WHERE PigeonLoft.loft_id = Pigeon.loft_id
            AND PigeonLoft.established_date < '2020-01-01' -- Голубятни, созданные до 2020 года
    );

DELETE FROM Pigeon
WHERE breed = 'Racing'
   AND training_hours < 50;

DELETE FROM Pigeon
WHERE owner_id IN (
    SELECT employee_id
    FROM Employee
    WHERE department = 'Archived'
);

DELETE FROM Pigeon
WHERE pigeon_id IN (
    SELECT p.pigeon_id
    FROM Pigeon p
    -- Связь с голубятней
    JOIN PigeonLoft pl ON p.loft_id = pl.loft_id
    -- Связь с сотрудником
    JOIN Employee e ON p.owner_id = e.employee_id
    -- Проверка участия в соревнованиях (если таблица Competitions существует)
    LEFT JOIN Competitions c ON p.pigeon_id = c.pigeon_id AND c.date >= NOW() - INTERVAL '1 year'
    WHERE
        pl.capacity < 100
        AND e.department = 'Training'
        AND e.experience_years < 3
        AND c.pigeon_id IS NULL -- Не участвовал в соревнованиях
        AND p.flying_speed < (
            SELECT AVG(flying_speed)
            FROM Pigeon
            WHERE breed = p.breed
        )
);

-- from dml dir
UPDATE Pigeon
SET last_check_date = vc.check_date
FROM VetCheck vc
WHERE Pigeon.pigeon_id = vc.pigeon_id;

UPDATE Pigeon
SET status = 'Archived'
WHERE pigeon_id IN (
    SELECT p.pigeon_id
    FROM Pigeon p
    LEFT JOIN VetCheck vc ON p.pigeon_id = vc.pigeon_id
    WHERE vc.check_date < CURRENT_DATE - INTERVAL '6 months'
    OR vc.check_id IS NULL
);

UPDATE Pigeon
SET flying_speed = flying_speed * 1.10
WHERE breed IN (
    SELECT breed
    FROM PigeonBreeds
    WHERE category = 'Sport'
);
