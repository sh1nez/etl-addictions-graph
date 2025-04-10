-- Обновление емкости голубятни
CREATE OR REPLACE PROCEDURE UpdateLoftCapacity(
    target_loft_id INT,
    new_capacity INT)
LANGUAGE SQL
AS $$
    UPDATE PigeonLoft
    SET capacity = new_capacity
    WHERE loft_id = target_loft_id;
$$;

-- Автоназначение менеджера для новой голубятни
CREATE OR REPLACE PROCEDURE AutoAssignManager(new_loft_name VARCHAR(100), location TEXT)
LANGUAGE SQL
AS $$
    INSERT INTO PigeonLoft(loft_name, manager_id, location, capacity)
    SELECT
        new_loft_name,
        manager_id,
        location,
        100
    FROM Manager
    WHERE department = 'Operations'
    ORDER BY experience_years DESC
    LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION GetLoftsByLocation(location_pattern TEXT))
RETURNS SETOF PigeonLoft
LANGUAGE SQL
AS $$
    SELECT * FROM PigeonLoft
    WHERE location ILIKE '%' || location_pattern || '%';
$$;
