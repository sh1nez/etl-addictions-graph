CREATE TABLE PigeonLoft (
    loft_id SERIAL PRIMARY KEY,
    loft_name VARCHAR(100) NOT NULL,
    manager_id INT,
    location TEXT NOT NULL,
    capacity INT NOT NULL,
    established_date DATE,
    FOREIGN KEY (manager_id) REFERENCES Manager(manager_id)
);