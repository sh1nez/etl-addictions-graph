CREATE OR REPLACE PROCEDURE AddManager(
    f_name VARCHAR(50),
    l_name VARCHAR(50),
    b_date DATE,
    h_date DATE,
    sal DECIMAL(10,2),
    dept VARCHAR(100)
LANGUAGE SQL
AS $$
    INSERT INTO Manager(first_name, last_name, birth_date, hire_date, salary, department)
    VALUES (f_name, l_name, b_date, h_date, sal, dept);
$$;

CREATE OR REPLACE PROCEDURE RemoveOrphanedManagers()
LANGUAGE SQL
AS $$
    DELETE FROM Manager
    WHERE manager_id NOT IN (
        SELECT manager_id
        FROM PigeonLoft
        WHERE manager_id IS NOT NULL
    )
    AND department != 'Archived';
$$;

CREATE OR REPLACE FUNCTION GetManagersByDepartment(dept_name VARCHAR(100))
RETURNS SETOF Manager
LANGUAGE SQL
AS $$
    SELECT * FROM Manager
    WHERE department = dept_name;
$$;
