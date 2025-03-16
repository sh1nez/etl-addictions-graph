CREATE TABLE Employee (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    hire_date DATE NOT NULL,
    position VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    supervisor_id INT,
    department VARCHAR(100),
    experience_years INT,
    FOREIGN KEY (supervisor_id) REFERENCES Employee(employee_id)
);