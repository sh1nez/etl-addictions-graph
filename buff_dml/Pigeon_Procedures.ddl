CREATE OR REPLACE PROCEDURE UpdatePigeonRing(
    p_id INT,
    new_ring VARCHAR(20))
LANGUAGE SQL
AS $$
    UPDATE Pigeon
    SET ring_number = new_ring
    WHERE pigeon_id = p_id;
$$;

CREATE OR REPLACE PROCEDURE DeletePigeonsByColor(target_color VARCHAR(30))
LANGUAGE SQL
AS $$
    DELETE FROM Pigeon
    WHERE color = target_color;
$$;

CREATE OR REPLACE PROCEDURE InsertPigeon(
    p_name VARCHAR(50),
    p_breed VARCHAR(50),
    b_date DATE,
    l_id INT,
    owner_id INT,
    ring VARCHAR(20),
    clr VARCHAR(30),
    wgt DECIMAL(5,2),
    speed DECIMAL(5,2),
    tr_hours INT)
LANGUAGE SQL
AS $$
    INSERT INTO Pigeon(name, breed, birth_date, loft_id, owner_id, ring_number, color, weight, flying_speed, training_hours)
    VALUES (p_name, p_breed, b_date, l_id, owner_id, ring, clr, wgt, speed, tr_hours);
$$;

CREATE OR REPLACE FUNCTION GetPigeonsByBreed(target_breed VARCHAR(50)))
RETURNS SETOF Pigeon
LANGUAGE SQL
AS $$
    SELECT * FROM Pigeon
    WHERE breed = target_breed;
$$;
