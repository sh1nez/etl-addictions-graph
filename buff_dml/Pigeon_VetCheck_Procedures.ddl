CREATE OR REPLACE PROCEDURE insert_pigeon(
    p_name VARCHAR(50),
    p_breed VARCHAR(50),
    p_loft_id INT
) LANGUAGE SQL
AS $$
    INSERT INTO Pigeon (name, breed, loft_id)
    VALUES (p_name, p_breed, p_loft_id);
$$;

CREATE OR REPLACE PROCEDURE insert_vetcheck(
    p_pigeon_id INT,
    p_status TEXT
) LANGUAGE SQL
AS $$
    INSERT INTO VetCheck (pigeon_id, check_date, health_status)
    VALUES (p_pigeon_id, CURRENT_DATE, p_status);
$$;

CREATE OR REPLACE FUNCTION select_pigeon_checks()
RETURNS TABLE (
    pigeon_name VARCHAR(50),
    breed VARCHAR(50),
    health_status TEXT,
    check_date DATE
) LANGUAGE SQL
AS $$
    SELECT p.name, p.breed, vc.health_status, vc.check_date
    FROM Pigeon p
    JOIN VetCheck vc USING(pigeon_id);
$$;
