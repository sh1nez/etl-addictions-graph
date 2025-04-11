CREATE OR REPLACE PROCEDURE insert_pigeonloft(
    p_name VARCHAR(100),
    p_location TEXT
) LANGUAGE SQL
AS $$
    INSERT INTO PigeonLoft (loft_name, location)
    VALUES (p_name, p_location);
$$;

CREATE OR REPLACE PROCEDURE insert_manager(
    p_first_name VARCHAR(50),
    p_last_name VARCHAR(50)
) LANGUAGE SQL
AS $$
    INSERT INTO Manager (first_name, last_name)
    VALUES (p_first_name, p_last_name);
$$;

CREATE OR REPLACE FUNCTION select_loft_managers()
RETURNS TABLE (
    loft_name VARCHAR(100),
    location TEXT,
    manager_name TEXT
) LANGUAGE SQL
AS $$
    SELECT
        pl.loft_name,
        pl.location,
        CONCAT(m.first_name, ' ', m.last_name)
    FROM PigeonLoft pl
    LEFT JOIN Manager m USING(manager_id);
$$;
