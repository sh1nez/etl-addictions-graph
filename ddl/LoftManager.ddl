CREATE TABLE LoftManager (
    loft_id INT NOT NULL,
    manager_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    role_description TEXT,
    PRIMARY KEY (loft_id, manager_id),
    FOREIGN KEY (loft_id) REFERENCES PigeonLoft(loft_id),
    FOREIGN KEY (manager_id) REFERENCES Manager(manager_id)
);