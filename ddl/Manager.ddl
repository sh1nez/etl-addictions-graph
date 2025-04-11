CREATE TABLE Manager (
    manager_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    department VARCHAR(100),
    experience_years INT,
    specialization VARCHAR(100)
);

-- from dml dir
UPDATE Manager
SET salary =
    CASE
        WHEN experience_years > 10 THEN salary * 1.20
        WHEN experience_years > 5 THEN salary * 1.15
        ELSE salary * 1.10
    END
WHERE department = 'Operations';

INSERT INTO Manager (first_name, last_name, department, salary)
SELECT
    nm.full_name,
    nm.last_name,
    nm.department,
    nm.base_salary
FROM NewManagers nm
LEFT JOIN Manager m ON nm.full_name = m.first_name AND nm.last_name = m.last_name
WHERE m.manager_id IS NULL;
