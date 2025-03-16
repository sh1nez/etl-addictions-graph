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