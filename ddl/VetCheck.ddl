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
