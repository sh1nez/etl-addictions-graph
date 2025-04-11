CREATE TABLE VetCheck (
    check_id SERIAL PRIMARY KEY,
    pigeon_id INT NOT NULL,
    check_date DATE NOT NULL,
    health_status TEXT NOT NULL,
    veterinarian VARCHAR(100),
    medication_given TEXT,
    next_checkup DATE,
    FOREIGN KEY (pigeon_id) REFERENCES Pigeon(pigeon_id)
);


-- from dml dir
INSERT INTO VetCheck (pigeon_id, check_date, health_status)
SELECT
    p.pigeon_id,
    CURRENT_DATE,
    'Pending'
FROM Pigeon p
LEFT JOIN VetCheck vc ON p.pigeon_id = vc.pigeon_id
WHERE vc.check_id IS NULL;

UPDATE VetCheck
SET health_status = 'Completed'
WHERE check_id IN (
    SELECT check_id
    FROM VetCheck
    WHERE check_date < CURRENT_DATE - INTERVAL '7 days'
    AND health_status = 'Pending'
);
