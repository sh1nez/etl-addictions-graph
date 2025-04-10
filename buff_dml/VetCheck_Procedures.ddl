CREATE OR REPLACE PROCEDURE AddVetCheck(
    p_id INT,
    h_status TEXT,
    vet_name VARCHAR(100))
LANGUAGE SQL
AS $$
    INSERT INTO VetCheck(pigeon_id, check_date, health_status, veterinarian)
    VALUES (p_id, CURRENT_DATE, h_status, vet_name);
$$;

CREATE OR REPLACE PROCEDURE DeleteChecksByStatus(status_filter TEXT))
LANGUAGE SQL
AS $$
    DELETE FROM VetCheck
    WHERE health_status = status_filter;
$$;

CREATE OR REPLACE FUNCTION GetChecksByStatus(status_filter TEXT))
RETURNS SETOF VetCheck
LANGUAGE SQL
AS $$
    SELECT * FROM VetCheck
    WHERE health_status = status_filter;
$$;
