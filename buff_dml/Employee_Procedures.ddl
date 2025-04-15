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

CREATE OR REPLACE PROCEDURE insert_employee(
    p_first_name VARCHAR(50),
    p_last_name VARCHAR(50),
    p_birth_date DATE,
    p_hire_date DATE,
    p_position VARCHAR(100),
    p_salary DECIMAL(10,2),
    p_department VARCHAR(100),
    p_experience INT
)
LANGUAGE SQL
AS $$
    INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department, experience_years)
    values( p_first_name, p_last_name, COALESCE(p_birth_date, cast(CURRENT_DATE as date)),
	COALESCE(p_hire_date, cast(CURRENT_DATE as date)), p_position, p_salary, p_department, p_experience);
$$;

CREATE OR REPLACE PROCEDURE update_employee(
	p_min_experience INT
)
LANGUAGE SQL
AS $$
    UPDATE Employee
    SET
        salary = salary * 1.1,
        position = CONCAT('Senior ', position)
    WHERE experience_years > p_min_experience;
$$;

CREATE OR REPLACE PROCEDURE delete_employees(
	p_department VARCHAR(100)
)
LANGUAGE SQL
AS $$
    DELETE FROM Employee
    WHERE department = p_department;
$$;

CREATE OR REPLACE PROCEDURE insert_where_employee(
	p_specialization VARCHAR
)
LANGUAGE SQL
AS $$
    INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department, experience_years)
    SELECT
        first_name,
        last_name,
        COALESCE(birth_date, cast(CURRENT_DATE as date)),
        cast(CURRENT_DATE as date),
        'Contractor',
        COALESCE(salary, 1) * 0.8,
        department,
        experience_years
    FROM Manager
    WHERE specialization = p_specialization;
$$;
