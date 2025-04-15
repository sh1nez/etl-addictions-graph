CREATE TABLE LoftManager (
    loft_id INT NOT NULL,
    manager_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    role_description TEXT,
    PRIMARY KEY (loft_id, manager_id)
);

CREATE OR REPLACE PROCEDURE update_where_LoftManager(
p_end_date date
)
LANGUAGE SQL
AS $$
    UPDATE LoftManager
    SET end_date = p_end_date
    WHERE start_date < p_end_date - INTERVAL '365 days';
$$;

CREATE OR REPLACE PROCEDURE update_LoftManager(
p_role_description TEXT
)
LANGUAGE SQL
AS $$
    UPDATE LoftManager
    SET role_description = UPPER(CAST(p_role_description AS VARCHAR));
$$;
CREATE OR REPLACE PROCEDURE delete_LoftManager(
p_role_description VARCHAR(50)
)
LANGUAGE SQL
AS $$
    DELETE FROM LoftManager
    WHERE cast(role_description AS VARCHAR) = p_role_description;
$$;
