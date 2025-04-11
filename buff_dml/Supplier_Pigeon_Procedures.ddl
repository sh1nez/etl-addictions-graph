CREATE OR REPLACE PROCEDURE insert_supplier(
    p_name VARCHAR(100)
) LANGUAGE SQL
AS $$
    INSERT INTO Supplier (name)
    VALUES (p_name);
$$;

CREATE OR REPLACE PROCEDURE link_pigeon_supplier(
    p_pigeon_id INT,
    p_supplier_id INT
) LANGUAGE SQL
AS $$
    UPDATE Pigeon
    SET supplier_id = p_supplier_id
    WHERE pigeon_id = p_pigeon_id;
$$;

CREATE OR REPLACE FUNCTION select_supplier_pigeons()
RETURNS TABLE (
    supplier_name VARCHAR(100),
    pigeon_name VARCHAR(50),
    breed VARCHAR(50)
) LANGUAGE SQL
AS $$
    SELECT s.name, p.name, p.breed
    FROM Supplier s
    JOIN Pigeon p USING(supplier_id);
$$;
