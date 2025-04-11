CREATE OR REPLACE PROCEDURE UpdateDeliveryTime(
    s_id INT,
    new_days INT))
LANGUAGE SQL
AS $$
    UPDATE Supplier
    SET delivery_time_days = new_days
    WHERE supplier_id = s_id;
$$;

CREATE OR REPLACE PROCEDURE DeleteSuppliersWithoutContact())
LANGUAGE SQL
AS $$
    DELETE FROM Supplier
    WHERE contact_person IS NULL;
$$;

CREATE OR REPLACE PROCEDURE InsertSupplier(
    s_name VARCHAR(100),
    contact VARCHAR(100),
    phone VARCHAR(20),
    s_email VARCHAR(100),
    addr TEXT,
    rtng DECIMAL(3,2),
    del_time INT)
LANGUAGE SQL
AS $$
    INSERT INTO Supplier(name, contact_person, phone_number, email, address, rating, delivery_time_days)
    VALUES (s_name, contact, phone, s_email, addr, rtng, del_time);
$$;

CREATE OR REPLACE FUNCTION GetSuppliersByMinRating(min_rating DECIMAL(3,2)))
RETURNS SETOF Supplier
LANGUAGE SQL
AS $$
    SELECT * FROM Supplier
    WHERE rating >= min_rating;
$$;
