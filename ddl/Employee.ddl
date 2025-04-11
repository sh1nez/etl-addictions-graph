CREATE PROCEDURE etl_employee_transforms
AS
BEGIN
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

    INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department, experience_years)
    Values('John', 'Doe', SYSDATETIME(), SYSDATETIME(), 'Analyst', 50000, 'Finance', 2);

	INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department, experience_years)
    Values('Jane', 'Smith', SYSDATETIME(), SYSDATETIME(), 'HR Specialist', 55000, 'HR', 3);

	INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department, experience_years, supervisor_id)
    SELECT m.first_name, m.last_name, m.birth_date, m.hire_date, 'Team Lead', m.salary + 1000, m.department, m.experience_years + 1, NULL
    FROM Manager m;

    UPDATE Employee
    SET salary = salary * 1.1,
        position = Concat('Senior ', position)
    WHERE experience_years > 5;

    DELETE FROM Employee
    WHERE department = 'Interns';

    INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department, experience_years)
    SELECT first_name, last_name, birth_date, SYSDATETIME(), 'Contractor', salary * 0.8, department, experience_years
    FROM Manager
    WHERE specialization = 'External';

    UPDATE Employee
    SET phone_number = CONCAT('+7-', phone_number)
    WHERE phone_number IS NOT NULL;

    DELETE FROM Employee
    WHERE salary < 30000;
	
	UPDATE Employee
    SET email = LOWER(email)
    WHERE email LIKE '%@example.com';

    DELETE FROM Employee
    WHERE position LIKE '%temp%';
END
GO
