CREATE TABLE Flight (
    flight_id SERIAL PRIMARY KEY,
    pigeon_id INT NOT NULL,
    date TIMESTAMP NOT NULL,
    distance_km DECIMAL(6,2) NOT NULL,
    duration_minutes INT NOT NULL,
    altitude_meters INT,
    FOREIGN KEY (pigeon_id) REFERENCES Pigeon(pigeon_id)
);
